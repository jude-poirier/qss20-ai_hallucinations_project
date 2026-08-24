# Docs

Reference material behind the analysis. The code goes in `../code/`, the numbers in `../output/`,
and the reasoning here.

| File | What it is |
|---|---|
| [`LABELING_CODEBOOK.md`](LABELING_CODEBOOK.md) | The decision rules behind every coded variable: the 0 to 4 severity ladder, actor coding, the eligibility filters, and worked edge cases. This is what the paper cites for how the coding was done. |
| [`VALIDATION.md`](VALIDATION.md) | How the coding was validated and where it falls short. Covers the regex attempt, the switch to LLM coding, and the hand-coded kappa. |
| [`CONTROL_CODING_BRIEF.txt`](CONTROL_CODING_BRIEF.txt) | A self-contained brief you paste into a fresh model window, with `controls_all_fulltext.csv` attached, to code the controls. Holds the codebook rules and the pitfalls that sank the regex. |

Start with the codebook if you want to know what a variable means, and with `VALIDATION.md` if you
want to know how much to trust it.
