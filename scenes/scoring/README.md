# Scoring — scenes

Reads every scene source in [`../sources/`](../sources) and produces the ranked Top 100 scenes.

## Run it

```bash
# one-time setup (from the repo root)
python3 -m venv .venv
.venv/bin/pip install -r scenes/scoring/requirements.txt

# score
.venv/bin/python scenes/scoring/score.py
```

Writes:
- [`../output/ranking.csv`](../output/ranking.csv) — full ranking of every scene, machine-readable
- [`../output/top-100.csv`](../output/top-100.csv) — top 100 only, same columns
- [`../output/top-100.md`](../output/top-100.md) — top 100 rendered for humans

The published `scene_name` and `description` columns default to what the
captured sources wrote (most common name; longest description). `scene-names.csv`
and `descriptions.csv` override them with editor-cleaned versions (source
attribution removed, em dashes cleared, name artifacts dropped) for any scene
listed there, leaving the captured sources untouched.

## Algorithm

```
per-mention score = tier × rank × engagement
raw_score         = sum of per-mention scores per normalized_scene_id
final_score       = raw_score × (1 + 0.5 × ln(num_sources))     # breadth bonus
```

- **tier** (articles only): top ×3, high ×2, mid ×1, low ×0.25, unknown ×0.25.
  Reddit / YouTube are never tier-weighted.
- **rank** (ranked lists): up to +50% for a scene near the top of a ranked list.
- **engagement**: articles ×1; Reddit `1 + ln(upvotes)/4`; YouTube `1 + ln(reach/3000)/4`.
- **breadth**: rewards a scene picked across many independent sources/threads.

Scenes whose film has no Dolby Atmos home mix are dropped via the shared
movie-side exclusion list [`../../scoring/excluded.txt`](../../scoring/excluded.txt),
joined on `normalized_title`.

`timestamps.csv` is a researched-timestamp override: a scene's `timestamp`
normally comes only from a captured source, but this file supplies figures
explicitly stated by external references for scenes no source dated (each row
cites its source). An override takes precedence over any source-derived timestamp.

Curve constants (`REDDIT_K`, `YT_K`, `YT_BASE`, `BREADTH_B`) are named at the top
of [`score.py`](score.py). See [`../docs/methodology.md`](../docs/methodology.md)
for the full rationale.
