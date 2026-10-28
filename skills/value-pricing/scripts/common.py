"""Shared helpers: load the study, resolve per-segment values, evaluate config expressions, write summaries."""
from __future__ import annotations

import argparse
import ast
import json
import operator
import subprocess
from datetime import date
from pathlib import Path

import numpy as np
import yaml

SKILL = Path(__file__).resolve().parent.parent


def study_arg(desc: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--study", default="pricing-study", help="study folder (holds study.yaml)")
    return ap


class Study:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        if not (self.root / "study.yaml").exists():
            raise SystemExit(f"{self.root}/study.yaml not found: copy {SKILL}/templates/study.yaml there first")
        self.cfg = yaml.safe_load((self.root / "study.yaml").read_text())
        self.bands = self.cfg["segments"]["bands"]
        self.segments = [b["id"] for b in self.bands]
        self.archetypes = self.cfg.get("archetypes", [])

    def path(self, *parts) -> Path:
        p = self.root.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def yaml(self, name: str, required: bool = True):
        p = self.root / name
        if not p.exists():
            if required:
                raise SystemExit(f"{p} not found: copy {SKILL}/templates/{Path(name).name} and fill it")
            return None
        return yaml.safe_load(p.read_text())

    def segment_share(self) -> dict:
        s = {b["id"]: float(b.get("share") or 0) for b in self.bands}
        tot = sum(s.values())
        return {k: (v / tot if tot else 1 / len(s)) for k, v in s.items()}

    def archetype_share(self, seg: str) -> dict:
        raw = {a["id"]: float(per_seg(a.get("share", 1.0), seg)) for a in self.archetypes}
        tot = sum(raw.values()) or 1.0
        return {k: v / tot for k, v in raw.items()}


def per_seg(v, seg):
    """A config value may be a scalar or a {segment: value} map."""
    if isinstance(v, dict):
        if seg in v:
            return v[seg]
        if "default" in v:
            return v["default"]
        raise KeyError(f"no value for segment {seg!r} in {v}")
    return v


def status(v):
    """A feature status from YAML: unquoted yes/no load as booleans, so normalise to "yes" | "partial" | "no" | None."""
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return None if v is None else str(v).strip().lower()


_BINARY_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow, ast.BitAnd: operator.and_, ast.BitOr: operator.or_,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg, ast.Not: np.logical_not, ast.Invert: operator.invert}
_COMPARE_OPS = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le,
    ast.Gt: operator.gt, ast.GtE: operator.ge,
}
_SAFE_NUMPY = {
    "abs": np.abs, "clip": np.clip, "exp": np.exp, "log": np.log,
    "maximum": np.maximum, "minimum": np.minimum, "sqrt": np.sqrt, "where": np.where,
}
_SAFE_RNG = {"lognormal"}
_SAFE_FUNCTIONS = {"abs": np.abs, "max": np.maximum, "min": np.minimum}


def _expression_node(node, ns):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, bool)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in _SAFE_FUNCTIONS:
            return _SAFE_FUNCTIONS[node.id]
        if node.id.startswith("_") or node.id not in ns:
            raise ValueError(f"unknown or forbidden name in value expression: {node.id}")
        return ns[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        return _BINARY_OPS[type(node.op)](_expression_node(node.left, ns), _expression_node(node.right, ns))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_expression_node(node.operand, ns))
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        values = [_expression_node(value, ns) for value in node.values]
        fn = np.logical_and if isinstance(node.op, ast.And) else np.logical_or
        result = values[0]
        for value in values[1:]:
            result = fn(result, value)
        return result
    if isinstance(node, ast.Compare):
        left = _expression_node(node.left, ns)
        results = []
        for op, comparator in zip(node.ops, node.comparators):
            if type(op) not in _COMPARE_OPS:
                raise ValueError("comparison operator is not allowed in value expressions")
            right = _expression_node(comparator, ns)
            results.append(_COMPARE_OPS[type(op)](left, right))
            left = right
        result = results[0]
        for value in results[1:]:
            result = np.logical_and(result, value)
        return result
    if isinstance(node, ast.IfExp):
        return np.where(_expression_node(node.test, ns), _expression_node(node.body, ns), _expression_node(node.orelse, ns))
    if isinstance(node, ast.Call):
        fn = _expression_node(node.func, ns)
        if not callable(fn) or node.keywords:
            raise ValueError("only positional calls to allowlisted functions are permitted in value expressions")
        args = [_expression_node(arg, ns) for arg in node.args]
        return fn(*args)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        if node.value.id == "np" and node.attr in _SAFE_NUMPY:
            return _SAFE_NUMPY[node.attr]
        if node.value.id == "rng" and node.attr in _SAFE_RNG and "rng" in ns:
            return getattr(ns["rng"], node.attr)
    if isinstance(node, ast.Name) and node.id in _SAFE_FUNCTIONS:
        return _SAFE_FUNCTIONS[node.id]
    raise ValueError(f"unsupported syntax in value expression: {type(node).__name__}")


def eval_expr(expr, ns: dict):
    """Evaluate the small arithmetic/NumPy expression language used by study YAML."""
    if isinstance(expr, (int, float)):
        return expr
    tree = ast.parse(str(expr), mode="eval")
    return _expression_node(tree.body, ns)


def git_sha(root: Path) -> str | None:
    """Read the study folder's current Git commit for summary provenance; no files are changed."""
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


HEADER = ("phase", "run_date", "currency", "fx", "git_sha", "assumptions", "gaps")


def write_summary(st: Study, phase: str, body: dict, assumptions: list[str] | None = None, gaps: list | None = None):
    out = {"phase": phase, "run_date": date.today().isoformat(), "currency": st.cfg.get("currency", "EUR"),
           "fx": st.cfg.get("fx"), "git_sha": git_sha(st.root), "assumptions": assumptions or [], "gaps": gaps or []}
    out.update(body)
    p = st.path(phase, "results", "summary.json")
    p.write_text(json.dumps(out, indent=2, default=_json_default))
    return p


def read_summary(st: Study, phase: str) -> dict | None:
    p = st.root / phase / "results" / "summary.json"
    return json.loads(p.read_text()) if p.exists() else None


def merge_summary(st: Study, phase: str, body: dict, assumptions=None, gaps=None):
    """Add keys to an existing summary, keeping what other scripts of the same phase wrote."""
    prev = read_summary(st, phase) or {}
    keep = {k: v for k, v in prev.items() if k not in HEADER}
    keep.update(body)
    return write_summary(st, phase, keep, assumptions or prev.get("assumptions"), gaps or prev.get("gaps"))


def _json_default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))
