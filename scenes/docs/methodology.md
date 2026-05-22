# Methodology — scenes ranking

> **Status:** live. Schema, capture workflow and scoring v1 are all in place. The algorithm is implemented in [`../scoring/score.py`](../scoring/score.py) (analogous to [`../../scoring/score.py`](../../scoring/score.py)); the published ranking is [`../output/top-100.md`](../output/top-100.md) with the full table in [`../output/ranking.csv`](../output/ranking.csv).

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

### Vague-mention rule

When a source praises a film generally without picking a specific scene, capture differently:

- **No scene at all** (source only names the film, no scene info) → **skip** in scenes/. The film-level signal is still preserved by the corresponding movie-side capture under `../../sources/`.
- **No timestamp and no description that identifies a specific scene** (e.g. "the entire film is great", "all race scenes") → **skip**. Same rationale.
- **Vague but resembles an existing captured scene** (e.g. source says "the flight scenes" when another source has picked a specific flight scene) → **ask the curator** before merging into the existing id or coining a new one. Don't silently merge — that overstates cross-source signal.

This rule was applied retroactively to source 003 (hifi.de) on 2026-05-21: 6 of 15 entries were removed because they were whole-film praise rather than specific scene picks. `list_length` for that source was adjusted from 15 to 9 to match what's actually captured.

### Scope: narrative feature films, Atmos only

This sub-project ranks scenes from **narrative feature films** that ship with a **Dolby Atmos mix**. Skip:

- **TV shows.** Episodes of TV series are out of scope for the *ranking*. Any TV scenes already captured stay in `sources/` (history isn't revised) but are dropped from the ranking by `score.py` via [`../scoring/tv-shows.txt`](../scoring/tv-shows.txt), joined on `normalized_title`.
- Standalone concert recordings / concert films (e.g. *Hans Zimmer Live in Prague*, *John Williams in Vienna*) — they may be Atmos and may be picked by demo sources, but they aren't narrative feature films.
- Music videos (e.g. Imagine Dragons "Radioactive").
- **Picks where a commenter or source explicitly flags the film as not Atmos** — e.g. "this is 5.1 DTS-HD MA only" or "this is DTS:X, not Atmos" or "you'll have to upmix this". These mentions could be revived later if/when the films get an Atmos remaster, but the demo recommendation is for a non-Atmos mix so it doesn't belong in the Atmos scenes ranking.

For films whose Atmos status isn't called out and isn't on the existing exclusion list, capture normally — scoring will filter via `scoring/excluded.txt` if needed.

Music-performance *scenes within a narrative film* are in scope (e.g. the Live Aid recreation in *Bohemian Rhapsody*, the "Shallow" performance in *A Star Is Born*), since the film itself is a narrative work.

**TV-episode naming convention** (for the captured-but-not-ranked TV sources): `{show-slug}-s{season}e{episode}` (e.g. `stranger-things-s5e8`, `archive-81-s1e8`). The `movie_title` field carries the human-readable form (`"Stranger Things Season 5, Ep. 8"`). Scene-id format unchanged: `{normalized_title}--{kebab-case scene name}`.

### Same-publication-snapshot rule

A single editorial voice making the same picks counts as **one source**, not multiple. Skip captures that fall into either of these patterns:

1. **Same article, different snapshot.** A continuously-updated article counted at multiple points in time (e.g. the 2022 vs 2025 version of What Hi-Fi's Atmos-scenes feature). Capture only the most recent version.
2. **Same creator, different medium, same picks.** A creator publishing the same scene list as both a blog post and a YouTube video (or vice versa). Capture only one — prefer the format with better engagement metadata or the one published first.

Distinct articles from the same publication, with different authors or substantively different picks, are still independent sources (e.g. CE Pro could publish two different articles by different authors covering different scenes — those are separate).

Applied retroactively on 2026-05-21:
- The 2022 What Hi-Fi pocketmags snapshot (22 entries) was identified as the ancestor of source 001 (42 entries) and skipped.
- Tanmay Mehta's YouTube video (Aug 3, 2023) was identified as the video version of his blog post (source 012, Aug 4, 2023) with identical 5 picks; the video was skipped in favor of the already-captured blog post.

### Multi-scene-per-film rule

When a single source entry mentions multiple distinct scenes within the same film, capture each scene as its own `scenes_mentioned[]` entry — don't lump them into one.

Examples:
- A source describes both the opening and the ISS-fire sequence in Gravity → two entries (`gravity--drifting-in-space` and `gravity--fire`).
- A source describes Hoth blizzard, Battle of Hoth (AT-ATs), and Dagobah swamp ambience all in one film entry → three entries.
- A source describes a two-part Insurgent scene that the author explicitly splits → two entries.

This sometimes makes `list_length` larger than the article's stated film count (the article picks N films but mentions M > N scenes). `list_length` reflects scenes captured, not films covered.

## Authority tiers

The shared [`../../docs/source-authority-tiers.md`](../../docs/source-authority-tiers.md) applies to scene sources too. A publication that's `top` for the movie ranking is `top` for the scene ranking — the editorial credibility doesn't change. One scene-side divergence: an **`unknown` (un-assessed) source is weighted as `low`** here (see Scoring below), not as neutral `mid`.

## Scoring (v1)

Implemented in [`../scoring/score.py`](../scoring/score.py); the published ranking is [`../output/top-100.md`](../output/top-100.md) with the full table in [`../output/ranking.csv`](../output/ranking.csv). The aggregation key is `normalized_scene_id`.

```
per-mention score = tier × rank × engagement
raw_score         = Σ per-mention scores for a scene
final_score       = raw_score × (1 + 0.5 × ln(num_sources))
```

**Tier** (articles only — Reddit/YouTube are never tier-weighted): `top` ×3, `high` ×2, `mid` ×1, `low` ×0.25, `unknown` ×0.25. `unknown` deliberately equals `low`: an un-vetted source is treated cautiously, not given neutral credit, until it is assessed upward.

**Rank** (ranked lists only): `1 + ((list_length − rank + 1) / list_length) × 0.5` — up to +50% for the top-ranked scene.

**Engagement** — articles ×1 (carried by tier instead); Reddit `1 + ln(upvotes)/4`; YouTube `1 + ln(reach/3000)/4` where `reach = video_views + channel_subscribers/10`. The `ln` curve is **bounded**: the most-upvoted Reddit comment in the pool (256 upvotes) scores ×2.4 and the biggest YouTube video ×2.3 — both below a `top`-tier article's ×3, so a single viral comment can never outrank vetted editorial coverage. (An earlier `sqrt(upvotes)` curve ran to ×16 and let one popular comment dominate.)

**Breadth** — `raw_score` is multiplied by `1 + 0.5 × ln(num_sources)`, where `num_sources` is the count of distinct source files (Reddit threads + articles + videos) that name the scene. `ln(1)=0`, so a single-source scene gets ×1.0 (no penalty); corroboration across many independent sources is rewarded with diminishing returns. This is what makes a scene picked across many threads outrank one a single long, popular comment happens to list.

**Exclusions** — scenes whose film has no Dolby Atmos home mix are dropped, by joining each scene's `normalized_title` against the shared movie-side [`../../scoring/excluded.txt`](../../scoring/excluded.txt). Every film captured in `sources/` was checked for an Atmos release (see [`../scoring/atmos-check.csv`](../scoring/atmos-check.csv)).

Tunable constants (`REDDIT_K`, `YT_K`, `YT_BASE`, `BREADTH_B`) are named at the top of `score.py`.

Resolved open questions:
- **Movie-side boost?** No — the scene and movie rankings stay fully independent.
- **Ranked vs unranked lists?** The movie-side rank multiplier (≤ +50%) is reused unchanged; being on a list at all is most of the signal.
- **Atmos exclusion?** Re-uses `../../scoring/excluded.txt`, joined on `normalized_title`.

## Relationship to the movie ranking

- **Independent outputs.** The scene ranking does not feed into, and is not derived from, the movie ranking.
- **Shared authority tiers.** Tier assignments in [`../../docs/source-authority-tiers.md`](../../docs/source-authority-tiers.md) apply to both.
- **Intentional source dupes.** Articles that cover both films and scenes (e.g. What Hi-Fi's scene roundup, AudioAdvice's top-10 scenes) are captured in [`../../sources/`](../../sources/) for their movie mentions and again here for their scene-level detail. The duplication is by design — different rankings, different units, same underlying article.

## Change log

Every change to the scene-side schema or scoring is recorded here.

- **2026-05-21** — Sub-project scaffolded. Templates, schema, methodology stub created. No sources captured yet; no scoring code yet.
- **2026-05-22** — Scene-id dedup curation pass. 48 sources / 410 unique scene ids reviewed; 10 duplicate-id pairs (the same scene captured under different ids) merged after curator approval — e.g. `gravity--opening` + `gravity--outside` → `gravity--drifting-in-space`, `mission-impossible-fallout--skydiving` → `--halo-jump`. 400 unique scenes remain.
- **2026-05-22** — Atmos verification. All 244 captured films checked for a Dolby Atmos home mix; 14 newly-confirmed non-Atmos films appended to `../../scoring/excluded.txt` (now 25 entries).
- **2026-05-22** — Scoring v1 implemented (`../scoring/score.py`). Mirrors the movie engine's tier/rank structure with three scene-side changes: (1) engagement uses a bounded `ln` curve instead of `sqrt`, so no single Reddit comment or YouTube video outranks a `top`-tier article; (2) a breadth multiplier `1 + 0.5·ln(num_sources)` rewards cross-source consensus; (3) `unknown`-tier sources are weighted as `low` (×0.25). Published ranking generated at `../output/top-100.md` and `../output/ranking.csv`.
- **2026-05-22** — Scope narrowed to **feature films only**. TV-show scenes are no longer ranked: 21 scenes across 14 shows (e.g. *Stranger Things*, *Game of Thrones*, *Andor*, *See*) are dropped via the new [`../scoring/tv-shows.txt`](../scoring/tv-shows.txt). They remain captured in `sources/`. Ranking went from 374 → 354 scenes.
- **2026-05-22** — Added `../scoring/descriptions.csv` and `../scoring/scene-names.csv`, editor-cleaned overrides for the published `scene_name` and `description` columns. They default to what the captured sources wrote (most common name; longest description); these files supply copy-edited versions (source attribution like "OP:" / "[outlet] pick" removed, em dashes cleared, name artifacts like "(Ch 6)" / "(Tokyo?)" dropped) without altering the captured sources. 51 descriptions and 8 names cleaned across the top 100.
- **2026-05-22** — Added `../scoring/timestamps.csv`, a researched-timestamp override. A scene's `timestamp` normally comes only from a captured source that stated one; this file supplies figures explicitly stated by external references (chapter databases, scene guides) for scenes no source dated — each row cites where the figure was stated. `score.py` applies an override in precedence over any source-derived timestamp. Seeded with two entries (`jurassic-park--t-rex-breakout-rain`, `a-quiet-place--raccoons-on-roof`).
