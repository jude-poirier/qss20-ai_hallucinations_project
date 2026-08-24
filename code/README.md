# Code

The analysis pipeline. Run the notebooks in numeric order, `00` through `05`. Each reads what an earlier one wrote, so the numbers are the run order. Launch Jupyter from this directory; every path
is relative (`../data/...`, `../output/...`) and nothing is hardcoded.

## Pipeline

```
data/raw/Charlotin-hallucination_cases.csv
      │  00_pull            load + profile missingness
data/interim/raw.pkl
      │  01_clean           US filter, severity/actor coding, caseload merge
data/interim/clean.pkl  +  data/coded/analysis_data_coded.csv   (AI arm)
      │
      │  02_build_controls  stream the CourtListener bulk file, keep eligible non-AI
      │                     sanctions opinions, write them with full text for coding
data/coded/controls_all_fulltext.csv  +  controls_validation_40.csv
      │
      │  (manual) code controls_all_fulltext.csv with an LLM
      │      (fresh window + docs/CONTROL_CODING_BRIEF.txt) -> controls_llm_coded.csv
      │
      │  03_build_pooled    dedupe + drop ineligible, stack controls under the AI arm
data/coded/pooled_coded.csv
      │
      │  04_analyze         AI-arm figures (A–D) + pooled AI-vs-non-AI comparison (E)
output/figures/*.png
      │
      │  05_validate_controls   score the LLM coder against your hand codes
output/figures/fig_validation_confusion.png  +  output/tables/validation_stats.txt
```

## The notebooks

| # | Notebook | Reads | Writes |
|---|---|---|---|
| 00 | `00_pull.ipynb` | `../data/raw/Charlotin-hallucination_cases.csv` | `../data/interim/raw.pkl` |
| 01 | `01_clean.ipynb` | `../data/interim/raw.pkl` | `../data/interim/clean.pkl`, `../data/coded/analysis_data_coded.csv` |
| 02 | `02_build_controls.ipynb` | `../data/raw/bulk-data/opinion-clusters-2026-06-30.csv.bz2` | `../data/coded/controls_all_fulltext.csv`, `controls_validation_40.csv` |
| 03 | `03_build_pooled.ipynb` | `controls_all_fulltext.csv`, `controls_llm_coded.csv`, `analysis_data_coded.csv` | `../data/coded/pooled_coded.csv` |
| 04 | `04_analyze.ipynb` | `../data/interim/clean.pkl`, `raw.pkl`, `../data/coded/pooled_coded.csv` | figures in `../output/figures/` |
| 05 | `05_validate_controls.ipynb` | `controls_validation_40_HANDCODED.csv` (your hand codes + LLM codes) | `../output/figures/fig_validation_confusion.png`, `../output/tables/validation_stats.txt` |

**00, pull.** Loads the Charlotin download, prints shape, columns, and per-column missingness.

**01, clean.** Filters to U.S. rows; codes `severity` (0 to 4), `actor`, `federal`, `tool_named`,
`field`; merges court-level caseload with a before/after row-count check. Writes both the pickled
frame the analysis uses and `analysis_data_coded.csv`, the AI arm the pooled builder reads.

**02, build controls.** Streams the ~2.3 GB CourtListener bulk file in chunks (it does not fit in
memory), keeps 2023–2026 opinions that ruled on a sanctions question, and drops AI-contaminated,
bar-discipline, and criminal community-control / licensing cases. Writes each surviving opinion with
a wide text window so it can be read and coded.

**LLM coding (manual, between 02 and 03).** Open `../docs/CONTROL_CODING_BRIEF.txt` in a fresh model
window, attach `controls_all_fulltext.csv`, and save the returned labels as
`../data/coded/controls_llm_coded.csv`. Regex on full opinions was tried first and plateaued
(held-out kappa 0.36), so the control severities are coded by an LLM; see `../docs/VALIDATION.md`.

**03, build pooled.** Collapses duplicate opinions, drops `llm_eligible == False`, and stacks the
LLM-coded controls under the AI arm with an `ai` dummy.

**04, analyze.** Sections A to D characterize the AI arm (accountability gradient, severity by
representation, an ordered logit with court-clustered SEs, and a scikit-learn severity classifier).
Section E runs the pooled AI-vs-non-AI regression and figures.

**05, validate.** Reads your hand-coded 40 (with LLM codes already attached) and reports Cohen's kappa with a confusion matrix. This is the measurement-validation step for the control coder.

## Two inputs the notebooks do not produce

- `../data/raw/bulk-data/opinion-clusters-2026-06-30.csv.bz2`, the CourtListener snapshot for `02`
  (git-ignored; see `../data/DOWNLOAD_LINKS.md`).
- `../data/coded/controls_llm_coded.csv`, your LLM coding of the controls, for `03` and `05`.

## `labeling/`

Shared coding infrastructure, not a pipeline step. `02`, `03`, and `04` import `label_lib`; the
scripts build and score the hand-coded validation sample. See `labeling/README.md`.

## Requirements

```bash
pip install pandas numpy scipy scikit-learn matplotlib
```
