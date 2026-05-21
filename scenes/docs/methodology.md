# Methodology — scenes ranking

> **Status:** schema and capture workflow defined; scoring algorithm not yet written. Once enough scene sources have been captured to see the data distribution, a `scenes/scoring/score.py` will be added (analogous to [`../../scoring/score.py`](../../scoring/score.py)) and the published ranking will land at `scenes/output/top-scenes.md`.

This sub-project ranks specific **Dolby Atmos demo scenes** (e.g. "Blade Runner 2049 — Las Vegas approach"), not whole films. It is fully separated from the movie ranking under [`../../sources/`](../../sources/) — sources collected here are only used for the scene ranking. The same article may legitimately appear in both places, captured once for movie mentions and once for scene-level detail.

## Scene-source schema

Each source file is YAML frontmatter. Source-type-specific fields (subreddit/upvotes, channel/views, etc.) mirror the movie-side templates so the eventual scoring engine can reuse the same engagement math.

The primary unit is a **scene**, not a film. One source file can list many scenes; multiple scenes from the same film become separate entries in `scenes_mentioned[]`.

```yaml
scenes_mentioned:
  - movie_title: "Blade Runner 2049"
    movie_year: 2017
    normalized_title: "blade-runner-2049"       # joins with the movie ranking
    scene_name: "Las Vegas approach"             # human-readable, from the source
    normalized_scene_id: "blade-runner-2049--las-vegas-approach"
    timestamp: "01:24:30"                        # or "HH:MM:SS-HH:MM:SS"; null if not given
    rank: 5                                      # null if the source doesn't rank scenes
    description: "Spinner flight into the dust-orange Vegas ruins; wide low-end and overhead pans."
```

### `normalized_scene_id` convention

`{normalized_title}--{kebab-case scene name}` (double-dash separator). Stable join key across sources that describe the same scene with different wording.

Manual curation is expected: when a second source picks the same scene with a different name (e.g. "Vegas arrival" vs "Las Vegas approach"), reuse the existing id rather than coining a new one. The double-dash makes the movie/scene boundary unambiguous when grepping.

## Authority tiers

The shared [`../../docs/source-authority-tiers.md`](../../docs/source-authority-tiers.md) applies to scene sources too. A publication that's `top` for the movie ranking is `top` for the scene ranking — the editorial credibility doesn't change.

## Scoring (deferred)

Likely to mirror the [movie methodology](../../docs/methodology.md) with one obvious adjustment: a **scene-rank multiplier** replaces the film-rank multiplier. The aggregation key is `normalized_scene_id` rather than `normalized_title`.

Open questions to settle once data exists:
- Should a scene whose film *also* ranks highly get a small movie-side boost, or should the two rankings stay fully independent? (Default: independent — that's the whole point of a separate ranking.)
- How heavily to weight ranked scene lists (e.g. AudioAdvice's top-10) vs unranked curated lists (e.g. What Hi-Fi's 42).
- Exclusion of scenes whose film lacks an Atmos home mix — likely re-use [`../../scoring/excluded.txt`](../../scoring/excluded.txt) by joining on `normalized_title`.

## Relationship to the movie ranking

- **Independent outputs.** The scene ranking does not feed into, and is not derived from, the movie ranking.
- **Shared authority tiers.** Tier assignments in [`../../docs/source-authority-tiers.md`](../../docs/source-authority-tiers.md) apply to both.
- **Intentional source dupes.** Articles that cover both films and scenes (e.g. What Hi-Fi's scene roundup, AudioAdvice's top-10 scenes) are captured in [`../../sources/`](../../sources/) for their movie mentions and again here for their scene-level detail. The duplication is by design — different rankings, different units, same underlying article.

## Change log

Every change to the scene-side schema or scoring is recorded here.

- **2026-05-21** — Sub-project scaffolded. Templates, schema, methodology stub created. No sources captured yet; no scoring code yet.
