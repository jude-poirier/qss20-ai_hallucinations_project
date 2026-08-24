"""
validate_llm.py  —  score the LLM coder against YOUR hand codes (human gold standard).

This is the non-circular check: the LLM coded the controls, you hand-code a sample, and we compare.
Make a copy of the LLM-coded file, keep ~40 rows, add a `hand_severity` column, code those 40
yourself against docs/LABELING_CODEBOOK.md, then run this.

Usage:
    python validate_llm.py --file controls_llm_hand40.csv
      (file must have columns: llm_severity, hand_severity)
"""
import argparse, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix, accuracy_score

def num(x):
    try: return int(float(x))
    except: return np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="controls_llm_hand40.csv")
    a = ap.parse_args()
    d = pd.read_csv(a.file)
    d["h"] = d["hand_severity"].map(num); d["m"] = d["llm_severity"].map(num)
    d = d.dropna(subset=["h", "m"])
    if len(d) < 2:
        print("Need at least a couple of rows with both hand_severity and llm_severity filled."); return
    h, m = d["h"].astype(int), d["m"].astype(int)
    print(f"n = {len(d)}")
    print(f"exact agreement : {accuracy_score(h, m):.2f}")
    print(f"within-1 tier    : {(abs(h-m)<=1).mean():.2f}")
    print(f"Cohen's kappa    : {cohen_kappa_score(h, m):.2f}")
    print(f"quad-weighted k  : {cohen_kappa_score(h, m, weights='quadratic'):.2f}")
    pos = h > 0
    if pos.sum():
        print(f"sensitivity on real sanctions: {(pos & (m>0)).sum()}/{pos.sum()}")
    print(f"false positives (llm>0, hand=0): {((m>0) & (h==0)).sum()}")
    print("confusion (rows=hand, cols=llm):")
    print(confusion_matrix(h, m, labels=[0,1,2,3,4]))
    print("\nkappa > ~0.7 = trustworthy; 0.6-0.7 = usable with caution; below = needs work.")

if __name__ == "__main__":
    main()
