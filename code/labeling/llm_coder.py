"""
llm_coder.py  —  code control opinions with an LLM instead of regex.

Why: regex on full opinions plateaued (held-out kappa ~0.36) because courts phrase an imposed
sanction too many ways, and the keyword frame kept leaking bar-discipline / criminal cases. An LLM
reads the whole passage and judges both (a) whether the case even belongs in the control pool and
(b) the severity tier. It must still be validated against YOUR hand codes (see validate_coding.py).

Runs on your machine with an API key (this environment has no network). Resumable: re-running skips
rows already coded. Writes incrementally so a crash doesn't lose work.

Usage:
    pip install anthropic pandas
    export ANTHROPIC_API_KEY=sk-...
    python llm_coder.py --in ../data/coded/controls_validation_200.csv --text-col text_for_coding \
                        --out ../data/coded/controls_llm_coded.csv
"""
import argparse, json, os, time
import pandas as pd

MODEL = "claude-haiku-4-5-20251001"   # cheap + fast for classification; use claude-sonnet-5 for more accuracy

def load_codebook():
    for p in ("../../docs/LABELING_CODEBOOK.md", "LABELING_CODEBOOK.md", "../docs/LABELING_CODEBOOK.md"):
        if os.path.exists(p):
            return open(p).read()
    return "(codebook file not found - pass the rules inline)"

SYSTEM = """You are coding U.S. court opinions for a research dataset on sanctions. Apply ONLY the
rules in the codebook the user provides. You are strict and literal: code what the court actually
DID in this opinion, not what was merely requested, discussed, or denied.

Return STRICT JSON, no prose, with exactly these keys:
{"eligible": true|false, "severity": 0|1|2|3|4, "confidence": "high"|"medium"|"low", "reason": "<=15 words"}

eligible=false when the case is NOT a Rule 11 / 1927 / inherent-authority style LITIGATION sanction
matter -- e.g. criminal community-control sentencing, licensing-board discipline, or a standalone
attorney/judicial bar-discipline proceeding. For ineligible cases still give your best severity.
severity: 0 none/denied/discussed-only, 1 warning, 2 procedural, 3 monetary, 4 professional/terminal
(bar referral, suspension, disqualification, dismissal/default as a sanction, contempt)."""

PROMPT = """CODEBOOK:
{codebook}

OPINION TEXT:
\"\"\"{text}\"\"\"

Return the JSON now."""

def code_one(client, codebook, text):
    msg = client.messages.create(
        model=MODEL, max_tokens=200, system=SYSTEM,
        messages=[{"role": "user", "content": PROMPT.format(codebook=codebook, text=str(text)[:8000])}])
    raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        d = json.loads(raw)
        return int(d.get("severity", 0)), bool(d.get("eligible", True)), d.get("confidence", ""), d.get("reason", "")
    except Exception:
        return None, None, "low", "unparseable: " + raw[:60]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--text-col", default="text_for_coding")
    ap.add_argument("--out", default="controls_llm_coded.csv")
    ap.add_argument("--id-col", default="case_name")
    a = ap.parse_args()

    from anthropic import Anthropic
    client = Anthropic()
    codebook = load_codebook()
    df = pd.read_csv(a.inp)

    done = set()
    if os.path.exists(a.out):
        done = set(pd.read_csv(a.out)[a.id_col].astype(str))
        print(f"resuming: {len(done)} already coded")

    rows = []
    for i, r in df.iterrows():
        cid = str(r[a.id_col])
        if cid in done:
            continue
        sev, elig, conf, why = None, None, "low", ""
        for attempt in range(4):
            try:
                sev, elig, conf, why = code_one(client, codebook, r[a.text_col]); break
            except Exception as e:
                if attempt == 3: why = f"api error: {e}"
                time.sleep(2 * (attempt + 1))
        rows.append({a.id_col: cid, "llm_severity": sev, "llm_eligible": elig,
                     "llm_confidence": conf, "llm_reason": why})
        # write incrementally
        pd.DataFrame(rows).to_csv(a.out, mode="a", header=not os.path.exists(a.out), index=False)
        rows = []
        if (i + 1) % 25 == 0:
            print(f"  coded {i+1}/{len(df)}")
    print(f"done -> {a.out}")

if __name__ == "__main__":
    main()
