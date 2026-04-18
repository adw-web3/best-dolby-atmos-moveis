# Scoring

Reads every source file in [`../sources/`](../sources) and produces the ranked Top 100.

## Run it

```bash
# one-time setup
python3 -m venv .venv
.venv/bin/pip install -r scoring/requirements.txt

# score
.venv/bin/python scoring/score.py
```

Writes:
- [`../output/ranking.csv`](../output/ranking.csv) — full ranking of every film, every column machine-readable
- [`../output/top-100.md`](../output/top-100.md) — top 100 rendered for humans

## Algorithm

```
score_per_mention = tier_multiplier × rank_multiplier × engagement_multiplier
aggregate_score   = sum across all mentions of the same normalized_title
```

See [`../docs/methodology.md`](../docs/methodology.md) for the full rationale behind the weights.
