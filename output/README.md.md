# Output

Figures built by [`../code/04_analyze.ipynb`](../code/04_analyze.ipynb) (the AI-arm figures and the
pooled comparison) and [`../code/05_validate_controls.ipynb`](../code/05_validate_controls.ipynb)
(the coder validation). Re-running those notebooks rebuilds everything here.

```
output/
├── figures/    the PNGs below
└── tables/     validation_stats.txt
```

Sections A to D describe the AI arm, the documented AI-hallucination cases. That part is a
characterization of those cases. Section E and the validation figure cover the AI-vs-non-AI
comparison, which runs off `../data/coded/pooled_coded.csv`. See [`../data/README.md`](../data/README.md)
and [`../docs/LABELING_CODEBOOK.md`](../docs/LABELING_CODEBOOK.md) for how the coded variables were
built, and [`../docs/VALIDATION.md`](../docs/VALIDATION.md) for how far to trust them.

## AI-arm figures

### `figures/fig_accountability_gradient.png`
The headline. Stacked bars showing, for each responsible actor (lawyers n=719, pro se litigants
n=1,079, judges n=27), the share of cases ending in each consequence type: professional discipline,
monetary penalty, a case/ruling remedy, a warning, or nothing recorded.

The three actors get met by different responses. Lawyers draw personal penalties (discipline plus
money) in about 44% of cases. Pro se litigants mostly get warned. When a judge is the source, the
modal response is undoing the ruling and leaving the judge alone. It uses the full database (all
countries) so the small judge group has enough cases to show at all, so treat the judge cell as
indicative only.

### `figures/fig_severity_dist.png`
Observed sanction-severity distribution (tiers 0 to 4) for pro se (n=763) against counseled (n=496)
U.S. cases. Pro se cases pile up at tier 1 (warning). Counseled cases spread into the procedural,
monetary, and professional/terminal tiers.

### `figures/fig_forest.png`
Ordered logistic regression of severity on representation and controls, odds ratios with
court-clustered 95% CIs on a log scale. `pro_se` sits near 0.32 for reaching a higher severity
tier. Federal courts trend slightly higher. Severity trends down over time (`year_c`). No legal
field separates from the baseline.

### `figures/fig_ml_importance.png`
Permutation importance (drop in macro-F1) from a scikit-learn classifier predicting severity.
`pro_se` and `tool_named` carry most of the signal. Legal field and year contribute little or
nothing. Read this as which features matter, and read the confusion matrix for whether the model
predicts well at all.

### `figures/fig_ml_confusion.png`
Row-normalized confusion matrix for that classifier. It predicts "warning" for almost everything
(the warning row is 0.86, and the other rows leak heavily into the warning column), so severity is
only weakly predictable from these case features. This is a negative result, and it is the
interesting one. Sanction severity is largely not a function of observable case characteristics,
which reinforces that who the actor is matters more than what the case contains.

## Pooled comparison figures

### `figures/fig_pooled_means.png`
Mean severity by arm, AI against non-AI control. Read alongside the base-rate caveat in the root
README and `docs/VALIDATION.md`.

### `figures/fig_pooled_forest.png`
OLS coefficients from the pooled model, severity on the `ai` dummy plus controls, with 95% CIs.

## Validation

### `figures/fig_validation_confusion.png`
Agreement between the LLM control coder and an independent hand-coded sample of 40 controls. Cohen's
kappa is 0.87. `tables/validation_stats.txt` has the full numbers.

## Caveats that apply to every figure

- Associational, not something to read as causal. Representation and AI use are not randomly assigned.
- Coded severity is a reading of free text. The AI arm and the LLM control coder both validate at
  kappa 0.87 (see `docs/VALIDATION.md`).
- Detected cases only. The data records fabrications that were caught. Nothing here can bound how
  many went unseen.
- Judges: n=27 (8 U.S.), so that part of the gradient is a first look, not an estimate.
