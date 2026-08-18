# Docs

Methods documentation.

| File | What it is |
|---|---|
| [`LABELING_CODEBOOK.md`](LABELING_CODEBOOK.md) | The decision rules behind every coded variable — what counts as each severity tier, how `pro_se` and `field` are decided, what disqualifies a control. The authoritative source for how the data were coded. |

The codebook and the keyword lists in `../code/labeling/label_lib.py` must stay in sync. If you
change a rule, change it in both places — the codebook is what the paper cites, and the code is
what actually ran.

Related, but living next to what they describe:

- [`../code/labeling/README.md`](../code/labeling/README.md) — how to run the coding and
  validation workflow.
- [`../data/README.md`](../data/README.md) — dataset inventory, column dictionary, provenance.
- [`../output/README.md`](../output/README.md) — what each figure shows and its caveats.
