# Data

Every dataset in the project: where it came from, what each column means, and how the coded
variables were produced. The coding *rules* live in
[`../docs/LABELING_CODEBOOK.md`](../docs/LABELING_CODEBOOK.md); this file is the inventory and
the column dictionary.

## Layout

```
data/
├── raw/        downloads, never modified
│   ├── Charlotin-hallucination_cases.csv
│   └── bulk-data/       CourtListener snapshot, ~2.3 GB, git-ignored
├── interim/    rebuildable intermediates (raw.pkl, clean.pkl) — git-ignored
└── coded/      analysis-ready files with derived variables
    ├── analysis_data_coded.csv
    ├── controls_coded.csv
    └── pooled_coded.csv
```

The split is deliberate: `raw/` is what was downloaded, `interim/` is anything a notebook can
regenerate in seconds, `coded/` is what the analysis and the paper actually cite. If a file in
`interim/` is lost, re-run notebooks 00–01. If a file in `raw/` is lost, re-download it — and
note that the new download will not match the row counts below.

## Inventory

| File | Rows | What it is | Produced by |
|---|---|---|---|
| `raw/Charlotin-hallucination_cases.csv` | 1,848 | Raw download of Damien Charlotin's AI Hallucination Cases Database, unmodified. | Download |
| `raw/bulk-data/opinion-clusters-2026-06-30.csv.bz2` | ~10M | CourtListener opinion-clusters bulk snapshot. **Not in the repo.** | Download |
| `interim/raw.pkl` | 1,848 | Pickled Charlotin data. | `00_pull.ipynb` |
| `interim/clean.pkl` | 1,279 | U.S. rows with derived variables, analysis columns only. | `01_clean.ipynb` |
| `coded/analysis_data_coded.csv` | 1,279 | The AI arm — U.S. Charlotin rows plus derived variables. | `01_clean.ipynb` |
| `coded/controls_coded.csv` | ~1,067 | The control arm — non-AI sanctions cases from CourtListener, coded through the same pipeline. | `02_build_controls.ipynb` |
| `coded/pooled_coded.csv` | ~2,300 | Both arms stacked with an `ai` dummy (1 = AI case, 0 = control). The file the pooled regression reads. | `02_build_controls.ipynb` |

## Provenance and snapshots

- **Charlotin AI Hallucination Cases Database** — <https://www.damiencharlotin.com/hallucinations/>.
  Hand-curated by a single maintainer; no published codebook and no reported inter-rater
  reliability. Downloaded **2026-08-18** (not updated by the maintainer since download).
  Treated as a case-*finding* source, not as ground truth.
- **CourtListener bulk data** (Free Law Project) — <https://www.courtlistener.com/help/api/bulk-data/>,
  `opinion-clusters` file, snapshot **2026-06-30**, downloaded **2026-08-18**. Public domain.

Both are dated snapshots. Re-downloading later yields different row counts — cite these dates.

## Not in the repo

The CourtListener bulk file (~2.3 GB) is git-ignored; GitHub rejects files over 100 MB. To
rebuild the control arm, download the `opinion-clusters` snapshot into `data/raw/bulk-data/`
and run `code/02_build_controls.ipynb`. Instructions are at the top of that notebook and in
[`../code/labeling/README.md`](../code/labeling/README.md).

## Column dictionary — `coded/analysis_data_coded.csv` (AI arm)

Original Charlotin fields, kept as-is:

- `Case Name`, `Court`, `State(s)`, `Date` — as recorded by Charlotin. `State(s)` is really a
  *country* field; this file keeps only its "USA" rows.
- `Party(ies)` — the party responsible for the AI-fabricated material.
- `AI Tool` — the tool implicated where identified (often "Implied" or blank).
- `Legal Field Primary` — Charlotin's legal-area label.
- `Outcome` — the court's disposition, as free text. **This is the field the severity coder reads.**
- `Professional Sanction`, `Monetary Penalty`, `Hallucination Items`, `Pointer`, `Source` — as recorded.

Derived variables added by this project (see the codebook for rules):

| Column | Type | Definition |
|---|---|---|
| `year` | int | Filing year, from `Date`. |
| `year_c` | int | `year` centered at 2025. |
| `actor` | str | Responsible party collapsed to `Pro se`, `Counseled`, or `Judge`. |
| `pro_se` | 0/1 | 1 if pro se, 0 if counseled, blank for judges/other. |
| `federal` | 0/1 | 1 if the `Court` string looks like a U.S. federal court. |
| `tool_named` | 0/1 | 1 if a specific AI tool is named — not "Implied"/"Unidentified"/blank. |
| `field` | str | `Legal Field Primary` collapsed to the six most common areas plus `other`. |
| `court_caseload` | int | Number of cases from the same `Court` in this dataset. |
| `severity` | 0–4 | Ordinal sanction severity coded from `Outcome`: 0 none, 1 warning, 2 procedural, 3 monetary, 4 professional/terminal. Most severe tier present wins. |
| `consequence_lever` | str | The single most *personal* consequence recorded: professional discipline / monetary / case-ruling remedy / warning only / none. |

## Column dictionary — `coded/controls_coded.csv` and `coded/pooled_coded.csv`

| Column | Definition |
|---|---|
| `case_name`, `date_filed`, `year` | From the CourtListener opinion cluster. |
| `ai` | 1 for AI cases (pooled file only), 0 for controls. |
| `severity` | Same 0–4 ladder, coded from the opinion's disposition text. **See limitation 2.** |
| `pro_se` | From the cluster's `attorneys` field, falling back to pro-se markers in the text; blank when neither resolves. **See limitation 3.** |
| `field` | From the cluster's Nature-of-Suit string. |
| `federal` | Left blank for controls — court/jurisdiction lives in a separate bulk file not joined here. |
| `nature_of_suit` | Raw NOS string (controls) or `Legal Field Primary` (AI rows). |
| `text_excerpt` | First ~300 characters of the disposition text, for spot-checking. |

## Known limitations — read before using

1. **The coded variables are keyword codings of free text, not ground truth.** `severity`,
   `field`, and `pro_se` come from rule-based matching. They need validation against a
   hand-coded sample — `code/labeling/make_handcoding_sample.py` then `validate_coding.py`,
   reporting Cohen's kappa. That number is not yet in the repo.

2. **The severity coder behaves differently on the two arms.** It was built for Charlotin's
   short `Outcome` field. Run against full CourtListener opinions it over-fires to tier 4,
   because a keyword like "dismiss" or "referral" appearing anywhere in a long opinion triggers
   it. The control severity distribution is therefore **provisional and skews severe**. Restrict
   the coder to the sanctions region of the opinion (`label_lib.locate_sanction_region`) and
   re-run before comparing severity across arms.

3. **Representation is missing for most controls.** CourtListener's `attorneys` field is usually
   empty, so `pro_se` resolves for only a small fraction of controls. Do not use it as a control
   variable on that arm.

4. **Selection.** Both arms are *detected, reported* cases only. Charlotin contains no non-AI
   cases by construction; CourtListener skews federal and appellate. Undetected fabrications are
   invisible in both, and there is no way to bound how many there are.

5. **Not causal.** Representation and AI use are not randomly assigned. Every coefficient
   describes an association, not an effect.
