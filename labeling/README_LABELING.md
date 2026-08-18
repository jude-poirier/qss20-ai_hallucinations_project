# Labeling workflow

A toolkit for coding both arms of the AI-vs-non-AI comparison the same way, then proving
how reliable the coding is. Read `LABELING_CODEBOOK.md` first; it holds the actual rules.

## Files
- `LABELING_CODEBOOK.md` — the decision rules (what counts as each severity tier, pro se, etc.).
- `label_lib.py` — the automated coder. One pipeline for both arms.
- `make_handcoding_sample.py` — draws a stratified sample and writes a blank hand-coding template.
- `validate_coding.py` — scores the auto coder against your hand codes (accuracy, Cohen's kappa).
- `00b_build_controls_offline.ipynb` — builds the non-AI control group from a downloaded CourtListener bulk file (no API).

## Steps

### 1. Read the codebook and freeze the rules
Open `LABELING_CODEBOOK.md`. If you disagree with a rule, change it now, in the file, before
you code anything. The rules in the codebook and the keywords in `label_lib.py` must match.

### 2. Pull the two groups of opinions
- **AI arm:** you already have these in Charlotin. For rigor, follow each row's `Pointer`/`Source`
  link and fetch the actual opinion text, so both arms are coded from opinions, not summaries.
- **Control arm:** query CourtListener for opinions in the same 2023–2026 window that ruled on a
  sanctions / Rule 11 / § 1927 / inherent-authority question but do not involve AI. Pull the
  opinion text and, where available, the docket's Nature-of-Suit code and attorney fields.
  (This is the APIs module. I can write the pull notebook separately; it needs a free API token
  and has to be run where there is network.)

### 3. Filter the controls for contamination
Run `label_lib.is_ai_contaminated(text)` on every control and drop the ones that trip it. A
"non-AI" opinion that mentions hallucinated citations is a mislabeled AI case, not a control.

### 4. Auto-code everything
Run `label_lib.code_case(text, ai_flag, nos_code=..., docket_attorney_present=...)` over both
arms to get `severity`, `pro_se`, `field`, `contaminated`. This is fast and reproducible, and
it is the coding you will actually use in the regression.

### 5. Build the ground-truth sample
```bash
python make_handcoding_sample.py --n 90 --seed 20
```
This writes `handcoding_template.csv`: ~90 cases, stratified so every severity tier appears,
with the text to read and blank `hand_severity`, `hand_pro_se`, `hand_field`, `confidence`, `note`.

### 6. Hand-code the sample against the codebook
Fill the blank columns yourself, reading each opinion and applying the codebook. Mark
`confidence = low` whenever you had to infer representation or field from prose. If a second
coder does a slice independently, you also get inter-rater reliability on the human codes.

### 7. Validate the auto coder against your hand codes
```bash
python validate_coding.py --filled handcoding_template.csv --full-opinion
```
(Drop `--full-opinion` if `text_to_read` is Charlotin's short field rather than a full opinion.)
Report the numbers it prints. Rule of thumb: quadratic-weighted kappa above ~0.7 on severity means
you can lean on the automated coding; below ~0.6 means code that variable by hand or fix the rules.

### 8. Fix, or fall back
If a variable validates poorly, either tighten the keywords in `label_lib.py` and re-validate,
or code that variable entirely by hand.

### 9. Freeze and analyze
Once the coding validates, lock the coded file, note the Charlotin download date, and run the
pooled regression: severity on an AI dummy plus your controls. The AI coefficient is the answer to
the reviewer's question.

## A realistic minimum
Coding all four variables well is a week-plus of work, and representation status may not reach a
trustworthy kappa. A defensible minimum: code `severity`, the `ai` flag, `field` from the NOS code,
and federal/state, skip `pro_se` for the controls, and run the severity-on-AI-dummy regression on
that. It answers the core question without betting the result on the hardest variable to code.
