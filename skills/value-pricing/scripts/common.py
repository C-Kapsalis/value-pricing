"""Shared helpers: load the study, resolve per-segment values, evaluate config expressions, write summaries."""
from __future__ import annotations

import argparse
import json
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


def eval_expr(expr, ns: dict):
    """Evaluate a config expression over numpy arrays. The config files are the owner's own, not untrusted input."""
    if isinstance(expr, (int, float)):
        return expr
    return eval(str(expr), {"np": np, "__builtins__": {"min": min, "max": max, "abs": abs}}, ns)


def git_sha(root: Path) -> str | None:
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
