# Data

Every dataset in the project: where it came from, what the columns mean, and how the coded
variables were made. The decision rules live in [`../docs/LABELING_CODEBOOK.md`](../docs/LABELING_CODEBOOK.md).
This file is the inventory and the column dictionary. Download links are in
[`DOWNLOAD_LINKS.md`](DOWNLOAD_LINKS.md).

**No data is committed.** Everything here is git-ignored. The folders are kept with `.gitkeep` so
the structure is visible.

## Files and where they live

| File | Location | Rows | What it is |
|---|---|---|---|
| `Charlotin-hallucination_cases.csv` | `raw/` | 1,848 | Raw download of the AI Hallucination Cases Database, unmodified. |
| `opinion-clusters-2026-06-30.csv.bz2` | `raw/bulk-data/` | ~10M | CourtListener bulk snapshot. Stays compressed; pandas reads `.bz2` directly. |
| `raw.pkl`, `clean.pkl` | `interim/` | 1,848 / 1,279 | Rebuildable intermediates from notebooks 00 and 01. |
| `analysis_data_coded.csv` | `coded/` | 1,279 | The U.S. Charlotin rows with derived variables. The AI arm. Written by 01. |
| `controls_all_fulltext.csv` | `coded/` | ~hundreds | Eligible non-AI control opinions with a wide text window for coding. Written by 02. |
| `controls_llm_coded.csv` | `coded/` | ~797 | LLM severity and eligibility codes for the controls. Made by coding the file above in a model window. |
| `pooled_coded.csv` | `coded/` | AI + controls | AI arm and controls stacked with an `ai` dummy. Written by 03. |
| `controls_validation_40_HANDCODED.csv` | `coded/` | 40 | Independent hand codes plus LLM codes for the validation sample. Read by 05. |

## Provenance and snapshots

The Charlotin database is hand-curated by a single maintainer, with no published codebook or
inter-rater reliability. Downloaded 2026-08-18 and not updated by the maintainer since. It is a
case-finding source, treated as such, not as ground truth.

The CourtListener bulk file is the `opinion-clusters` snapshot dated 2026-06-30, downloaded
2026-08-18. Free Law Project data, public domain.

Both are dated snapshots. Re-downloading later gives different row counts, so cite these dates.

## Column dictionary: `analysis_data_coded.csv` (AI arm)

Original Charlotin fields kept as-is: `Case Name`, `Outcome`, `AI Tool`, `Legal Field Primary`,
`Party(ies)`, `Date`, and others.

Derived variables (see the codebook):

- `year` filing year.
- `actor` responsible party collapsed to `Pro se`, `Counseled`, or `Judge`.
- `pro_se` 1 if pro se, 0 if counseled, blank for judges and other.
- `federal` 1 if the court string looks federal, else 0.
- `tool_named` 1 if a specific AI tool is named.
- `field` legal area collapsed to the common categories plus `other`.
- `severity` ordinal 0 to 4 (0 none, 1 warning, 2 procedural, 3 monetary, 4 professional/terminal),
  coded from `Outcome`.

## Column dictionary: control and pooled files

- `case_name`, `year` from the CourtListener cluster.
- `ai` 1 for AI cases, 0 for controls.
- `severity` same 0 to 4 scale. For controls it comes from the LLM coder (`llm_severity`).
- `llm_eligible` False marks a case that is not a Rule 11-style litigation sanction. Those are
  dropped when building the pooled file.
- `field` from the Nature-of-Suit string.
- `text_for_coding` the opinion window the coder reads. In `controls_all_fulltext.csv` only.

## Known limitations

- The coded variables are readings of free text. `severity` needs validation against hand codes.
  The AI arm and the LLM control coder both come in at kappa 0.87. See
  [`../docs/VALIDATION.md`](../docs/VALIDATION.md).
- Representation is missing for most controls, so `pro_se` works as a control variable only on the
  AI arm.
- Both arms record detected cases only.
- The AI arm is curated and the controls are trigger-matched, a base-rate difference that sits in
  the study design. The comparison is associational.
