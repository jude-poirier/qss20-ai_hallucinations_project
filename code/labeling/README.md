# Labeling toolkit

The coding infrastructure shared across the pipeline, plus the machinery for measuring how reliable
that coding is. The decision rules live in `../../docs/LABELING_CODEBOOK.md` — read that first; this
file is the how-to-run.

The goal: code the AI cases and the control cases as alike as possible, and be able to say with a
number how much to trust each coded variable.

## Files

| File | What it is |
|---|---|
| `label_lib.py` | The coder. `code_severity` (0–4), `code_pro_se`, `field_from_nos`, plus the control-frame filters `is_ai_contaminated`, `is_bar_discipline`, `is_criminal_or_licensing`. Imported by notebooks 02–04. |
| `make_handcoding_sample.py` | Draws a stratified sample across severity tiers and writes a blank hand-coding template. |
| `validate_coding.py` | Scores the regex coder against hand codes (accuracy, within-1, Cohen's kappa). |
| `validate_llm.py` | Scores the LLM coder against hand codes. Same idea, for the LLM path. |
| `llm_coder.py` | Optional: codes controls via the Anthropic API if you have a key. Not needed if you code in a chat window instead. |

## Two coding paths in `label_lib.code_severity`

- **Short-outcome path** (`is_full_opinion=False`) — reads Charlotin's terse `Outcome` field for the
  AI arm. Any tier keyword present sets that tier. Validated at kappa 0.87 on its own sample.
- **Full-opinion path** (`is_full_opinion=True`) — reads a full control opinion. A keyword appearing
  anywhere is not enough (opinions mention "dismiss"/"discipline" incidentally), so it requires a
  sanctions region, no denial language, and an imposition cue near the sanction type.

On full opinions the regex path still plateaued (held-out kappa 0.36), so the controls are coded by
an LLM instead; the regex coder remains here as the documented first attempt. See
`../../docs/VALIDATION.md`.

## Control-frame filters

Not every opinion that mentions "sanction" is a comparable control. `label_lib` drops three kinds:

- `is_ai_contaminated` — a "non-AI" opinion that mentions hallucinated citations is a mislabeled AI case.
- `is_bar_discipline` — standalone attorney/judicial discipline proceedings are a different population.
- `is_criminal_or_licensing` — criminal "community-control sanctions" (a sentencing term) and
  licensing-board matters are not Rule 11-style litigation sanctions.

Notebook 02 applies all three when it builds the control set.

## Validation workflow

1. Notebook 02 writes `controls_validation_40.csv`, a 40-row sample with the text to read and a
   blank `hand_severity` column.
2. Hand-code those 40 yourself against the codebook. This is the independent human check — the coder
   (LLM) cannot also be the validator.
3. Notebook 05 (or `validate_llm.py`) merges your codes with the LLM codes and reports the kappa.

Rule of thumb: quadratic-weighted kappa above ~0.7 means the coded variable can carry weight in the
paper; below ~0.6 means fix the rules or code by hand.

## Keeping rules in sync

The keyword lists in `label_lib.py` and the rules in `../../docs/LABELING_CODEBOOK.md` must match.
If you change one, change the other — the codebook is what the paper cites, the code is what ran.
