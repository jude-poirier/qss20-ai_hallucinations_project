# Download links

The raw data isn't committed to the repo (the CourtListener file is ~2.3 GB and git-ignored). Download it into the paths below to reproduce the pipeline.

## Charlotin AI Hallucination Cases Database (the AI arm)

https://www.damiencharlotin.com/hallucinations/

Download the CSV from that page and place it at:

`data/raw/Charlotin-hallucination_cases.csv`

Snapshot used here: downloaded 2026-08-18 (the maintainer updates it over time, so re-downloading later will give a different row count).

## CourtListener bulk data (the control arm)

Bulk-data page: https://www.courtlistener.com/help/api/bulk-data/

Download the opinion-clusters file and place it at:

`data/raw/bulk-data/opinion-clusters-2026-06-30.csv.bz2`

Leave it compressed — the notebook reads `.bz2` directly. Or pull it from the public bucket with the free AWS CLI (no account needed):

```
aws s3 cp s3://com-courtlistener-storage/bulk-data/opinion-clusters-2026-06-30.csv.bz2 data/raw/bulk-data/ --no-sign-request
```

Snapshot used here: opinion-clusters 2026-06-30, downloaded 2026-08-18. Free Law Project data, public domain. The dockets and opinions bulk files are also available on that page if you later need court/jurisdiction fields or full opinion text, but this project only uses opinion-clusters.
