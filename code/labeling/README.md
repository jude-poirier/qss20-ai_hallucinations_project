# Labeling toolkit

Coding infrastructure shared by both arms of the AI-vs-non-AI comparison, plus the machinery
for proving how reliable that coding is.

**Read [`../../docs/LABELING_CODEBOOK.md`](../../docs/LABELING_CODEBOOK.md) first** — it holds
the actual decision rules. This file is the how-to-run.

The whole point of this directory: code the AI cases and the control cases the *same* way, from
the *same* kind of source, so an "AI vs non-AI" comparison isn't contaminated by differences in
how the two groups were labeled.

## Files

| File | What it is |
|---|---|
| `label_lib.py` | The automated coder. One pipeline for both arms: `code_severity`, `code_pro_se`, `field_from_nos`, `is_ai_contaminated`, `code_case`. |
| `make_handcoding_sample.py` | Draws a stratified sample across severity tiers and writes a blank hand-coding template. |
| `validate_coding.py` | Scores the auto coder against your hand codes — accuracy, within-1-tier, Cohen's kappa. |

`label_lib.py` is imported by `../02_build_controls.ipynb`. The two scripts are standalone and
are run from this directory.

## Workflow

### 1. Freeze the rules
Open the codebook. If you disagree with a rule, change it *now*, before coding anything. The
rules in the codebook and the keyword lists in `label_lib.py` must stay in sync — if you edit
one, edit the other.

### 2. Pull the two groups
- **AI arm** — already in the Charlotin data. For rigor, follow each row's `Pointer`/`Source`
  link and fetch the actual opinion text, so both arms are coded from opinions rather than from
  someone's summary of an opinion.
- **Control arm** — `../02_build_controls.ipynb` does this offline from the CourtListener bulk
  snapshot: 2023–2026 opinions ruling on a sanctions / Rule 11 / § 1927 / inherent-authority
  question that do not involve AI, with the Nature-of-Suit code and attorney fields where
  available.

### 3. Screen the controls for contamination
`label_lib.is_ai_contaminated(text)` runs on every control; anything it trips is dropped. A
"non-AI" opinion that mentions hallucinated citations is a mislabeled AI case, not a control.
This happens inside notebook 02.

### 4. Auto-code both arms
`label_lib.code_case(text, ai_flag, nos_code=..., docket_attorney_present=...)` returns
`severity`, `pro_se`, `field`, `contaminated`. Fast, reproducible, and this is the coding the
regression actually uses.

### 5. Build the ground-truth sample
```bash
python make_handcoding_sample.py --n 90 --seed 20
```
Writes `handcoding_template.csv`: ~90 cases stratified so every severity tier appears, with the
text to read plus blank `hand_severity`, `hand_pro_se`, `hand_field`, `confidence`, `note`.

Point `--csv` at the controls file and set `--text-col` to the opinion-text column to build the
same template for the control arm.

### 6. Hand-code it
Fill the blank columns yourself, reading each case and applying the codebook. Mark
`confidence = low` whenever you had to infer representation or field from prose. If a second
coder does a slice independently, you also get inter-rater reliability on the *human* codes,
which is worth reporting.

### 7. Validate
```bash
python validate_coding.py --filled handcoding_template.csv --full-opinion
```
Drop `--full-opinion` when `text_to_read` is Charlotin's short `Outcome`/`Details` field rather
than a full opinion — the coder behaves differently on the two and the flag matters.

Rule of thumb: quadratic-weighted kappa above ~0.7 on severity means you can lean on the
automated coding in the paper. Below ~0.6 means fix the rules or code that variable by hand.

### 8. Fix, or fall back
If a variable validates poorly: tighten the keywords in `label_lib.py` and re-validate, or code
that variable entirely by hand. Do not report a coefficient resting on a variable with a kappa
you would not defend out loud.

### 9. Freeze and analyze
Lock the coded file, note the Charlotin download date, and run the pooled regression: severity
on an AI dummy plus controls. That AI coefficient is the answer to the reviewer's question.

## Known issue: the coder over-fires on full opinions

`label_lib.py` was tuned on Charlotin's short `Outcome` field. Run against full CourtListener
opinions it over-assigns tier 4, because a keyword like "dismiss" or "referral" appearing
*anywhere* in a long document triggers it. `locate_sanction_region()` exists to address this by
slicing a window around the first sanctions trigger — confirm every severity call on the
control arm goes through it before comparing severity across arms. The current control severity
distribution is provisional and skews severe.

## A realistic minimum

Coding all four variables well is a week-plus of work, and representation status may never reach
a trustworthy kappa on the control arm. A defensible minimum: code `severity`, the `ai` flag,
`field` from the NOS code, and federal/state; skip `pro_se` for the controls; run the
severity-on-AI-dummy regression on that. It answers the core question without betting the
result on the hardest variable to code.
