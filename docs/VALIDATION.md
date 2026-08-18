# Validation status

Checked the control severity coder against 40 hand-coded control opinions. Cohen's kappa was 0.20, which is too low to rely on. Raw agreement was higher (0.75) but that's mostly because both the coder and I labeled most cases "no sanction," and kappa removes that easy agreement. On the cases that actually had a sanction imposed, the coder only caught 2 of 8.

Two reasons for the low score. First, on full opinion text the coder misses real sanctions because courts phrase them in more ways than the keywords cover — it missed a default judgment, a monetary deposition sanction, a discovery dismissal, a contempt order, and a judicial suspension. Second, the control pool is contaminated: a lot of the cases the trigger pulled in aren't litigation sanctions at all, mainly criminal "community-control sanctions" (a sentencing term) plus some licensing-board and judicial-conduct matters.

The second-coder pass was done by Claude Opus 4.8 (High), so it's a provisional machine check rather than independent human coding. I'm treating 0.20 as a sign the control side needs work, not as a final number.

Next steps: tighten the control frame to drop criminal community-control sanctions and licensing/judicial-discipline cases, and improve sanction detection in full opinions, then re-run the validation. The number that goes in the paper will come from that re-run, not this one.

If the control comparison can't be made reliable in time, the project still stands on the within-AI analysis, which doesn't need the control group — the accountability gradient, the severity-by-representation results, and the AI-arm coder (kappa 0.87). There's more within-AI work available there if needed.

For now the AI vs non-AI comparison is on hold until the control coding is fixed and re-validated. Any pooled figures in `output/` are provisional and shouldn't be read as results.
