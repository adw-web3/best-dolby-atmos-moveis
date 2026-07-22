# Scoring — TV show ranking

Aggregates every source under [`../sources/`](../sources/) and produces the ranked list.

## Run

From the repo root (reuses the repo's venv):

```bash
.venv/bin/python tv-shows/scoring/score.py
```

Writes:

- `../output/ranking.csv` — every show, full table
- `../output/top-50.csv` / `../output/top-50.md` — the published Top 50
- `atmos-check.csv` — verification worksheet, refreshed every run (curator-entered `is_atmos` / `platform` / `notes` values are preserved)

## Algorithm (v1)

```
per-mention score = tier × rank × engagement
raw_score         = Σ per-mention scores for a show
final_score       = raw_score × (1 + 0.5 × ln(num_sources))
```

Same engine as the scenes ranking (see [`../docs/methodology.md`](../docs/methodology.md) for constants and rationale), aggregated on `normalized_title` (whole series). Forum posts (`source_type: forum-post`) score at flat ×1.0 engagement — community voices without an upvote system.

## Exclusions

`excluded.txt` — this list's own file — drops shows verified to have no Dolby Atmos mix. It is populated by the curator after external verification against `atmos-check.csv`; entries that match no captured show trigger a warning (slug typo guard).
