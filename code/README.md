# Code

The analysis pipeline. Run the notebooks in numeric order: each one reads what the previous
one wrote. All paths are relative to this directory, so launch Jupyter from here (or from the
repo root — the notebooks use `../data/...` style paths).

## Pipeline

```
data/raw/Charlotin-hallucination_cases.csv
        │
        ▼  00_pull.ipynb            load + profile missingness
   data/interim/raw.pkl
        │
        ▼  01_clean.ipynb           US filter, severity/actor coding, caseload merge
   data/interim/clean.pkl ──────────────────────┐
        │                                       │
        │  (AI arm exported to                  │
        │   data/coded/analysis_data_coded.csv) │
        ▼                                       │
   02_build_controls.ipynb                      │
   + data/raw/bulk-data/  (2.3 GB, not in repo) │
        │                                       │
        ▼                                       ▼
   data/coded/controls_coded.csv           03_analyze.ipynb
   data/coded/pooled_coded.csv                  │
                                                ▼
                                        output/figures/*.png
```

## The notebooks

| Notebook | Reads | Writes |
|---|---|---|
| `00_pull.ipynb` | `../data/raw/Charlotin-hallucination_cases.csv` | `../data/interim/raw.pkl` |
| `01_clean.ipynb` | `../data/interim/raw.pkl` | `../data/interim/clean.pkl` |
| `02_build_controls.ipynb` | `../data/raw/bulk-data/opinion-clusters-2026-06-30.csv.bz2`, `../data/coded/analysis_data_coded.csv` | `../data/coded/controls_coded.csv`, `../data/coded/pooled_coded.csv` |
| `03_analyze.ipynb` | `../data/interim/clean.pkl`, `../data/interim/raw.pkl` | `../output/figures/*.png` |

**00 — pull.** Loads the Charlotin download, prints shape and column list, and reports percent
missing per column so the missingness is documented before anything is dropped.

**01 — clean.** Filters to the U.S. rows, then applies user-defined coding functions for
`severity` (ordinal 0–4), `actor`, `federal`, `tool_named`, and `field`. Merges court-level
caseload back onto the case rows, printing row counts before and after and asserting the count
is unchanged — an unmatched-key check, not just a merge.

**02 — build controls.** The control arm. Streams the CourtListener bulk file in 100k-row
chunks (it does not fit in memory), keeps 2023–2026 opinions that rule on a sanctions question,
drops any opinion that mentions AI-fabricated citations (a "non-AI" opinion that does is a
mislabeled AI case, not a control), and codes the survivors through `labeling/label_lib.py` —
the *same* coder used on the AI arm, which is the point. Prints a filter funnel at each stage.

**03 — analyze.** Three passes: the accountability-gradient figure, a proportional-odds ordered
logit with court-clustered standard errors written directly in NumPy/SciPy, and a scikit-learn
severity classifier benchmarked against a most-frequent baseline with permutation importance.

## `labeling/`

Shared coding infrastructure, not a pipeline step. Notebook 02 imports `label_lib`; the two
scripts build and score a hand-coded validation sample. See [`labeling/README.md`](labeling/README.md).

## Requirements

```bash
pip install pandas numpy scipy scikit-learn matplotlib
```

Notebook 02 also needs the CourtListener bulk file in `../data/raw/bulk-data/`. The other three
run against what is committed in the repo.
