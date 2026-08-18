# Labeling codebook

One page of rules. `label_lib.py` implements exactly these; if you change a rule here,
change it there too. The goal is that a second coder, given only this document and the
opinions, would produce the same labels you do.

## Scope and unit
- **Unit:** one court case (one opinion or order that resolves the sanctions question).
- **Both arms are coded from the underlying opinion text**, not from any summary. For the
  AI arm, follow Charlotin's `Pointer`/`Source` link to the opinion and code that. Do not
  code from Charlotin's `Outcome` field for the final analysis; use it only as a cross-check.

## Variables

### `ai` (0/1) — assigned, not coded
1 for cases drawn from Charlotin. 0 for control cases. Before accepting a control as 0,
run the contamination filter (below) and drop any that trip it.

### `severity` (0–4, ordinal) — assign the MOST SEVERE consequence present
- **0 None** — sanctions motion denied; no sanction imposed; apology accepted without penalty.
- **1 Warning** — verbal warning, admonishment, caution, reprimand, expressed displeasure, no further action.
- **2 Procedural / corrective** — filing or brief struck; argument waived or forfeited; order to
  show cause; mandatory CLE; certification or disclosure requirement; forced correction or refiling.
- **3 Monetary** — fine, monetary sanction, adverse costs, attorney's-fee award, disgorgement.
- **4 Professional / terminal** — bar or disciplinary referral; suspension; disqualification;
  pro hac vice revocation; dismissal or default entered as a sanction; contempt; vexatious-litigant
  or filing bar.
- **Rule:** if several apply, code the highest tier. First find the sanctions passage in the
  opinion (look for "Rule 11", "§ 1927", "inherent authority", "sanction", "show cause",
  "disciplinary", "referral"), then code within that passage.

### `pro_se` (1 / 0 / blank) — of the party responsible for the filing
Decide in this order and stop at the first that resolves:
1. **Docket attorney field** — party has no attorney of record on the relevant filing → 1; has one → 0.
2. **Text markers** — "pro se", "self-represented", "in propria persona", "appearing without counsel" → 1.
3. **Sanctioned actor is the attorney** → the party was counseled → 0.
4. **Otherwise leave blank.** Do not guess. Blank is a valid, honest code.

### `field` — legal area
1. **Federal Nature-of-Suit (NOS) code** if the docket has one → map via the NOS table.
2. Else keyword/manual → one of: contract, civil rights, tort, employment, administrative,
   family, bankruptcy, immigration, IP, habeas, tax, other.

## Contamination filter (controls only)
A "non-AI" control that mentions AI-fabrication markers ("hallucinat", "fabricated citation",
"nonexistent case", "ChatGPT", "generative AI", "LLM", a named chatbot) is not a clean control.
Drop it. This keeps undetected AI cases out of the zero group.

## Control-group frame (what counts as an eligible non-AI case)
Not a random draw from all litigation. Draw from cases in the **same 2023–2026 window** where a
court **ruled on a sanctions / Rule 11 / § 1927 / inherent-authority question** for reasons other
than AI. This holds "a sanctionable issue was litigated" roughly constant so the AI dummy is not
just picking up "this case had a sanctions fight at all."

## Confidence flags
For every coded case record a `confidence` in {high, medium, low} and a free-text `note`.
Mark `low` whenever you fell back to text inference for representation or field. Report how much
of the sample is low-confidence.
