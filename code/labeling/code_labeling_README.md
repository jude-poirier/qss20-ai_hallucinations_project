# Labeling toolkit

The coding infrastructure the pipeline shares, plus the machinery for measuring how far to trust
that coding. The decision rules live in [`../../docs/LABELING_CODEBOOK.md`](../../docs/LABELING_CODEBOOK.md).
Read that first. This file is the how-to-run.

The goal is to code the AI cases and the control cases the same way, and to put a number on how
reliable each coded variable is.

## Files

| File | What it is |
|---|---|
| `label_lib.py` | The coder. `code_severity` (0 to 4), `code_pro_se`, `field_from_nos`, and the control-frame filters `is_ai_contaminated`, `is_bar_discipline`, `is_criminal_or_licensing`. Imported by notebooks 02 to 04. |
| `make_handcoding_sample.py` | Draws a stratified sample across severity tiers and writes a blank hand-coding template. |
| `validate_coding.py` | Scores the regex coder against hand codes (accuracy, within-1, Cohen's kappa). |
| `validate_llm.py` | Scores the LLM coder against hand codes. Same idea, for the LLM path. |
| `llm_coder.py` | Optional. Codes controls through the Anthropic API if you have a key. Not needed if you code in a chat window. |

## Two coding paths in `label_lib.code_severity`

The function switches on `is_full_opinion`.

With `is_full_opinion=False` it reads Charlotin's terse `Outcome` field for the AI arm. The field
is the outcome, so any tier keyword present sets that tier. That path validated at kappa 0.87.

With `is_full_opinion=True` it reads a full control opinion. Here a keyword appearing anywhere is
not enough, because opinions mention "dismiss" and "discipline" in passing, so the path requires a
sanctions region, no denial language, and an imposition cue near the sanction type.

On full opinions even that stricter regex stalled (held-out kappa 0.36), so the controls are coded
by an LLM. The regex coder stays here as the documented first attempt. See
[`../../docs/VALIDATION.md`](../../docs/VALIDATION.md).

## Control-frame filters

Not every opinion that mentions "sanction" belongs in the control group. `label_lib` drops three
kinds, and notebook 02 applies all three:

- `is_ai_contaminated` catches a "non-AI" opinion that mentions hallucinated citations, which is a
  mislabeled AI case.
- `is_bar_discipline` catches standalone attorney and judicial discipline proceedings, a different
  population.
- `is_criminal_or_licensing` catches criminal community-control sanctions (a sentencing term) and
  licensing-board matters, which are not Rule 11-style litigation sanctions.

## Validation workflow

1. Notebook 02 writes `controls_validation_40.csv`, a 40-row sample with the text to read and a
   blank `hand_severity` column.
2. Hand-code those 40 yourself against the codebook. This is the independent human check. The
   coder cannot also be the validator.
3. Notebook 05 merges your codes with the LLM codes and reports the kappa.

Rule of thumb: quadratic-weighted kappa above about 0.7 means the coded variable can carry weight
in the paper. Below about 0.6 means fix the rules or code by hand.

## Keeping rules in sync

The keyword lists in `label_lib.py` and the rules in the codebook have to match. Change one, change
the other. The codebook is what the paper cites and the code is what ran.
