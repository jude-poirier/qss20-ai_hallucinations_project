# Who Gets Punished for AI Hallucinations?

**QSS 20 — Modern Statistical Computing · Final Project · Jude Poirier**

When someone files a court document containing a fabricated, AI-generated citation, what
happens to them — and does it depend on who they are? This project answers that with the
[AI Hallucination Cases Database](https://www.damiencharlotin.com/hallucinations/), maintained
by Damien Charlotin, and a non-AI control group built from
[CourtListener](https://www.courtlistener.com/help/api/bulk-data/) bulk data.

Three kinds of filers appear often enough to compare: attorneys, self-represented (pro se)
litigants, and judges. They are treated very differently. Roughly a quarter of attorney cases
end in personal professional discipline. Pro se litigants usually get a warning and little
else. When the hallucination comes from the bench, the court fixes the ruling and leaves the
judge alone. That pattern says something specific about how sanctions work: the court's tools
are built around lawyers, so when the responsible party sits outside the bar, there is little
for the system to grab onto.

## Headline finding

![accountability gradient](output/figures/fig_accountability_gradient.png)

Across 719 attorney cases, 1,079 pro se cases, and 27 judge cases, the figure shows the most
serious *personal* consequence on record for each group. An ordered logistic regression backs
up the litigant comparison: pro se filers have about a third the odds of a counseled filer of
reaching a higher severity tier (odds ratio 0.32, 95% CI 0.25–0.41), and the result survives
clustering standard errors by court. A separate machine-learning pass shows severity is barely
predictable from case features at all — the only two variables carrying real weight are whether
the filer was pro se and whether the AI tool was named.

## Repository layout

```
qss20-ai_hallucinations_project/
├── README.md                    <- you are here
├── code/                        <- the analysis pipeline, run 00 -> 03
│   ├── README.md
│   ├── 00_pull.ipynb
│   ├── 01_clean.ipynb
│   ├── 02_build_controls.ipynb
│   ├── 03_analyze.ipynb
│   └── labeling/                <- coding toolkit the notebooks import
│       ├── README.md
│       ├── label_lib.py
│       ├── make_handcoding_sample.py
│       └── validate_coding.py
├── data/                        <- git-ignored; see "Data" below
│   ├── README.md
│   ├── raw/                     <- downloads, unmodified
│   │   └── bulk-data/           <- 2.3 GB CourtListener snapshot
│   ├── interim/                 <- rebuildable .pkl files
│   └── coded/                   <- analysis-ready CSVs
├── docs/
│   ├── README.md
│   └── LABELING_CODEBOOK.md     <- decision rules behind every coded variable
└── output/
    ├── README.md
    ├── figures/                 <- the five generated figures
    └── tables/
```

Each folder carries its own `*_README.md` explaining what belongs there.

## Notebooks

Run in order. Every path is relative to `code/`; nothing is hardcoded.

| # | Notebook | Input | What it does | Output |
|---|---|---|---|---|
| 00 | [`code/00_pull.ipynb`](code/00_pull.ipynb) | `data/raw/Charlotin-hallucination_cases.csv` | Loads the database and profiles it — shape, columns, per-column missingness. | `data/interim/raw.pkl` |
| 01 | [`code/01_clean.ipynb`](code/01_clean.ipynb) | `data/interim/raw.pkl` | Keeps the U.S. cases; codes the 0–4 severity scale, actor type, and model features from the free-text `Outcome`; merges court-level caseload with before/after row-count diagnostics. | `data/interim/clean.pkl` |
| 02 | [`code/02_build_controls.ipynb`](code/02_build_controls.ipynb) | `data/raw/bulk-data/`, `data/coded/analysis_data_coded.csv` | Streams the CourtListener bulk file in chunks, filters to 2023–2026 sanctions rulings, screens out AI-contaminated opinions, and codes the controls through the *same* pipeline as the AI arm. | `data/coded/controls_coded.csv`, `data/coded/pooled_coded.csv` |
| 03 | [`code/03_analyze.ipynb`](code/03_analyze.ipynb) | `data/interim/clean.pkl`, `data/interim/raw.pkl` | Builds the accountability-gradient figure, a proportional-odds ordered logit with court-clustered standard errors, and a scikit-learn severity classifier with permutation importance. | five figures in `output/figures/` |

The `code/labeling/` module is shared infrastructure rather than a pipeline step — notebook 02
imports `label_lib.py`, and the two scripts beside it build and score a hand-coded validation
sample. See [`code/labeling/README.md`](code/labeling/README.md) for that workflow and
[`docs/LABELING_CODEBOOK.md`](docs/LABELING_CODEBOOK.md) for the rules themselves.

## Output

All five figures live in [`output/figures/`](output/figures/) and are rebuilt end-to-end by
notebook 03. [`output/README.md`](output/README.md) describes what each one shows and the
caveats that apply.

| Figure | What it shows |
|---|---|
| `fig_accountability_gradient.png` | The headline: consequence type by responsible actor. |
| `fig_severity_dist.png` | Severity distribution, pro se vs. counseled. |
| `fig_forest.png` | Ordered logit odds ratios with court-clustered CIs. |
| `fig_ml_importance.png` | Permutation importance from the severity classifier. |
| `fig_ml_confusion.png` | Confusion matrix — the negative result. |

## Data

**No data files are committed to this repo.** Everything under `data/` is git-ignored; the
folder structure is preserved with `.gitkeep` files so you can see where each file belongs.
Full inventory, column dictionary, and provenance dates are in
[`data/README.md`](data/README.md).

To reproduce, download into the paths below:

| Dataset | Rows | Where it goes | Source |
|---|---|---|---|
| Charlotin AI Hallucination Cases | 1,848 | `data/raw/Charlotin-hallucination_cases.csv` | <https://www.damiencharlotin.com/hallucinations/> — "Download CSV" on the database page. |
| CourtListener `opinion-clusters` bulk snapshot, 2026-06-30 (~2.3 GB compressed) | ~10M | `data/raw/bulk-data/` | <https://www.courtlistener.com/help/api/bulk-data/> — leave it compressed, pandas reads `.bz2` directly. |
| Coded AI arm | 1,279 | `data/coded/analysis_data_coded.csv` | Rebuilt by notebooks 00–01. |
| Coded non-AI controls | ~1,067 | `data/coded/controls_coded.csv` | Rebuilt by notebook 02. |
| Pooled AI + control file | ~2,300 | `data/coded/pooled_coded.csv` | Rebuilt by notebook 02. |

The two raw downloads are dated snapshots — re-downloading later yields different row counts,
so cite the dates recorded in [`data/README.md`](data/README.md). The four derived
files are fully reproducible from the two raw ones by running the notebooks in order.

## Methods used (mapping to course modules)

- **Pandas / regex / user-defined functions** — loading, severity coding, actor coding.
- **Merging** — the court-caseload merge in `01` prints row counts before and after and asserts
  the row count is unchanged, with an explicit unmatched-key check.
- **Chunked I/O at scale** — `02` streams a 2.3 GB compressed file in 100k-row chunks rather
  than loading it into memory, with a printed filter funnel at each stage.
- **Supervised ML** — `03` trains a scikit-learn severity classifier against a most-frequent
  baseline and reports permutation importance and a normalized confusion matrix.
- **Statistics from scratch** — the ordered logit and its court-clustered standard errors are
  written directly in NumPy and SciPy rather than pulled from a package.
- **Measurement validation** — `code/labeling/` scores the automated coder against a
  hand-coded sample and reports Cohen's kappa.

## Reproducing

```bash
pip install pandas numpy scipy scikit-learn matplotlib
# then run the notebooks in code/ in order: 00 → 01 → 02 → 03
```

Notebook 02 additionally requires the CourtListener bulk file in `data/raw/bulk-data/`; the
other three run against what is committed here.

## Status — Milestone 2

The repo is set up and the pipeline runs start to finish, rebuilding every figure in
`output/figures/`. Known work remaining before the final paper:

1. **The severity scale needs hand-validation.** It is a keyword reading of free-text
   dispositions. `code/labeling/make_handcoding_sample.py` draws the stratified sample and
   `validate_coding.py` scores it; the kappa is not yet reported.
2. **The severity coder over-fires on the control arm.** It was tuned on Charlotin's short
   `Outcome` field, so on full CourtListener opinions a stray keyword anywhere in a long
   document can trigger a high tier. The control severity distribution is provisional until the
   coder is restricted to the sanctions region of the opinion.
3. **Representation is missing for most controls**, so `pro_se` cannot yet serve as a control
   variable on that arm.

Nothing here is causal — representation and AI use are not randomly assigned, and both arms
capture only fabrications that were *detected and written up*.
