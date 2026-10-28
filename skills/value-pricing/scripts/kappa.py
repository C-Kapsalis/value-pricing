#!/usr/bin/env python3
"""Phase 2 · inter-rater agreement per feature (Cohen's κ) between two codings of the same vendors.

  kappa.py --study S [--a market/data/vendor_features.csv] [--b market/data/vendor_features2.csv]

Writes market/data/kappa.csv: feature_id, n, agreement, kappa, prevalence in each coding, drop (κ < 0.6).
A low-κ feature with ≥ 0.9 agreement and ≤ 5% prevalence is a rare-feature artefact (κ is unstable when
almost everyone is 0): flagged apart, still dropped unless the owner rules otherwise. hedonic.py reads
the drop column.
"""
from __future__ import annotations

import pandas as pd

from common import Study, study_arg


def cohen(a, b):
    po = (a == b).mean()
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def main():
    ap = study_arg(__doc__.splitlines()[0])
    ap.add_argument("--a", default="market/data/vendor_features.csv")
    ap.add_argument("--b", default="market/data/vendor_features2.csv")
    ap.add_argument("--threshold", type=float, default=0.6)
    x = ap.parse_args()
    st = Study(x.study)
    A = pd.read_csv(st.root / x.a).set_index("vendor")
    B = pd.read_csv(st.root / x.b).set_index("vendor")
    common = A.index.intersection(B.index)
    rows = []
    for f in [c for c in A.columns if not c.endswith("__unclear") and c in B.columns]:
        a, b = A.loc[common, f].astype(int), B.loc[common, f].astype(int)
        k = cohen(a, b)
        agree, prev = float((a == b).mean()), max(a.mean(), b.mean())
        low = k != k or k < x.threshold
        rows.append({"feature_id": f, "n": len(common), "agreement": round(agree, 3), "kappa": round(k, 3) if k == k else None,
                     "prevalence_a": round(a.mean(), 3), "prevalence_b": round(b.mean(), 3),
                     "drop": bool(low), "rare_artefact": bool(low and agree >= 0.9 and prev <= 0.05)})
    df = pd.DataFrame(rows).sort_values("kappa")
    df.to_csv(st.path("market", "data", "kappa.csv"), index=False)
    print(f"{len(common)} vendors double-coded; median κ {df.kappa.median():.2f}; dropped {int(df['drop'].sum())} of {len(df)}")
    if df["drop"].any():
        print(df[df["drop"]].to_string(index=False))


if __name__ == "__main__":
    main()
