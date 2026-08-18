"""
make_handcoding_sample.py  —  build the ground-truth hand-coding template.

Draws a stratified random sample (across severity tiers, so every tier is represented)
from the Charlotin AI cases, and writes a CSV with the case identifiers + the source text
you'll read, plus BLANK columns for you to fill by hand. You hand-code this against the
codebook; validate_coding.py then scores the automated coder against your hand codes.

For the control arm, once you've pulled opinions from CourtListener, point --csv at that
file and set --text-col to the opinion-text column; the same template columns apply.

Usage:
    python make_handcoding_sample.py --n 90 --seed 20
"""
import argparse, pandas as pd, numpy as np, label_lib as L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="/mnt/user-data/uploads/Charlotin-hallucination_cases.csv")
    ap.add_argument("--text-col", default="Details")   # opinion text col for controls; Details here
    ap.add_argument("--n", type=int, default=90)
    ap.add_argument("--seed", type=int, default=20)
    ap.add_argument("--out", default="handcoding_template.csv")
    a = ap.parse_args()

    df = pd.read_csv(a.csv)
    if "State(s)" in df.columns:
        df = df[df["State(s)"] == "USA"].copy()

    # provisional auto-severity only to STRATIFY the sample (not a label)
    df["_text"] = (df[a.text_col] if a.text_col in df.columns else df.get("Outcome")).astype("string")
    df["_strat"] = df["_text"].apply(lambda t: L.code_severity(t, is_full_opinion=(a.text_col!="Outcome")))

    per = max(1, a.n // 5)
    picks = (df.groupby("_strat", group_keys=False)
               .apply(lambda g: g.sample(min(per, len(g)), random_state=a.seed)))
    picks = picks.sample(min(a.n, len(picks)), random_state=a.seed).reset_index(drop=True)
    picks["_text"] = picks["_text"].fillna("")

    out = pd.DataFrame({
        "case_id": picks.get("Case Name", pd.Series(range(len(picks)))),
        "court":   picks.get("Court", ""),
        "date":    picks.get("Date", ""),
        "source_link": picks.get("Pointer", picks.get("Source", "")),
        "text_to_read": picks["_text"].astype(str).str.slice(0, 1500).values,
        # ---- BLANK columns for the human coder (fill against the codebook) ----
        "hand_severity": "",     # 0-4
        "hand_pro_se": "",       # 1 / 0 / blank
        "hand_field": "",        # contract / civil rights / ... / other
        "confidence": "",        # high / medium / low
        "note": "",
    })
    out.to_csv(a.out, index=False)
    print(f"wrote {a.out}  ({len(out)} rows, stratified across severity tiers)")
    print("template columns:", list(out.columns))

if __name__ == "__main__":
    main()
