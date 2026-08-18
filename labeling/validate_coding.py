"""
validate_coding.py  —  score the automated coder against your hand codes.

Run AFTER you have filled hand_severity / hand_pro_se / hand_field in the template.
It runs label_lib on the same text, lines the auto codes up against your hand codes,
and reports accuracy (severity) and Cohen's kappa (all three), so you can say in the
paper how trustworthy each coded variable is. Kappa > 0.7 is the usual "trust it" line.

Usage:
    python validate_coding.py --filled handcoding_template.csv
"""
import argparse, pandas as pd, numpy as np
from sklearn.metrics import cohen_kappa_score, accuracy_score, confusion_matrix
import label_lib as L

def _num(x):
    try: return int(float(x))
    except: return np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--filled", default="handcoding_template.csv")
    ap.add_argument("--full-opinion", action="store_true",
                    help="set when text_to_read is full opinion text (controls); "
                         "omit for Charlotin's short Outcome/Details")
    a = ap.parse_args()
    df = pd.read_csv(a.filled)

    # auto-code from the same text the human read
    df["auto_severity"] = df["text_to_read"].apply(
        lambda t: L.code_severity(t, is_full_opinion=a.full_opinion))
    df["auto_pro_se"] = df["text_to_read"].apply(lambda t: L.code_pro_se(text=t))

    # only rows the human actually coded
    m = df["hand_severity"].apply(_num).notna()
    if m.sum() == 0:
        print("No hand codes found. Fill hand_severity / hand_pro_se / hand_field first."); return
    d = df[m].copy()
    hs = d["hand_severity"].apply(_num); as_ = d["auto_severity"]
    print(f"Validated on {len(d)} hand-coded cases.\n")

    print("SEVERITY (0-4)")
    print(f"  exact accuracy : {accuracy_score(hs, as_):.2f}")
    print(f"  within-1 tier  : {(abs(hs-as_)<=1).mean():.2f}")
    print(f"  weighted kappa : {cohen_kappa_score(hs, as_, weights='quadratic'):.2f}")
    print("  confusion (rows=hand, cols=auto):")
    print(confusion_matrix(hs, as_, labels=[0,1,2,3,4]))

    # pro se: compare only where BOTH are non-blank
    hp = d["hand_pro_se"].apply(_num); ap_ = d["auto_pro_se"]
    both = hp.notna() & ap_.notna()
    if both.sum() >= 2:
        print("\nPRO SE (1/0)")
        print(f"  agreement : {(hp[both]==ap_[both]).mean():.2f}  (n={int(both.sum())})")
        print(f"  kappa     : {cohen_kappa_score(hp[both], ap_[both]):.2f}")
    else:
        print("\nPRO SE: too few cases where both auto and hand are non-blank to score.")

    print("\nInterpretation: report these numbers in the paper. Any variable with kappa "
          "below ~0.6 should be treated cautiously or coded fully by hand.")

if __name__ == "__main__":
    main()
