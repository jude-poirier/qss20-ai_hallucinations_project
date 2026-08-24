# Validation

Both arms use the same 0 to 4 severity scale. This is how each side was coded and checked, and
where the limits are.

## AI arm

Coded from Charlotin's short `Outcome` field with the regex coder in `label_lib.py`. Checked
against a hand-coded sample of 40 at Cohen's kappa 0.87 (quadratic-weighted 0.95). Two early bugs
turned up in that check and got fixed: negation blindness ("no monetary sanctions imposed" reading
as monetary) and a phrasing gap ("referral to state bar" missing tier 4). This arm is solid.

## Control arm

Harder, and it took two tries.

The first attempt coded controls with the same regex against full opinions. It looked good in
sample (kappa 0.92) and then collapsed on a fresh held-out sample (kappa 0.36). That gap is
overfitting: tuning the keywords to one sample does not carry to the next. Two things drove it.
Full opinions phrase an imposed sanction in far more ways than keywords catch, so the coder missed
real sanctions (it caught 2 of 8 in the held-out set). And the trigger pulled in cases that are not
Rule 11-style litigation sanctions at all, mainly criminal community-control sentencing plus some
licensing-board and bar-discipline matters.

The fix had two parts. The frame got tightened: `label_lib.is_criminal_or_licensing` and
`is_bar_discipline` drop the non-comparable cases at the build stage in notebook 02. And the
severity coding moved to an LLM, which reads the whole passage instead of matching keywords.

The LLM coder was checked against an independent hand-coded sample of 40 controls. Cohen's kappa
came in at 0.87 (quadratic-weighted 0.89), exact agreement 0.94, with 2 disagreements out of the 33
that matched by name. One was off by a tier (a vexatious-litigant case coded 4 by hand and 3 by the
LLM). One was an LLM false positive, reading a declined sanctions motion as an imposed sanction.
The coder caught every sanction the hand-coding found.

The hand codes are an independent human check. The model that coded the controls did not also
validate them.

## What validation does not fix

A clean kappa says the controls were coded the way a human would. It does not close the gap in the
study design. The AI arm is a curated set, meaning cases where a sanction question was already
adjudicated, and the controls are trigger-matched opinions that are mostly non-events. That
base-rate difference biases any AI-vs-non-AI comparison on its own, apart from coding quality. The
pooled result is associational, and that caveat belongs next to it in the paper.

## Bottom line

- AI-arm severity coder: kappa 0.87. Ready.
- LLM control coder: kappa 0.87 against independent hand codes. Usable, with the base-rate caveat
  stated.
- The within-AI findings stand on their own and do not depend on the control group.
