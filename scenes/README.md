# Best Dolby Atmos Demo Scenes

Parallel sub-project of the [best Dolby Atmos movies ranking](../README.md). Same data-driven, auditable approach — but the ranked unit here is a **specific scene** (e.g. "Mad Max: Fury Road — sandstorm chase"), not a whole film.

## How it relates to the movie ranking

- **Independent output.** The scene ranking is generated separately and does not influence the movie top-100.
- **Separate sources.** Articles, posts, and videos captured under [`sources/`](sources/) are used only for the scene ranking. An article that covers both films *and* highlights specific scenes will be captured both here (for its scene picks) and in the movie-side [`../sources/`](../sources/) (for its film mentions). The duplication is intentional — different rankings, different units, same article.
- **Shared authority tiers.** [`../docs/source-authority-tiers.md`](../docs/source-authority-tiers.md) applies to both sub-projects.

## Layout

```
scenes/
  sources/          raw structured data, one file per source
    blog-articles/
    news-articles/
    reddit-posts/
    reddit-comments/
    youtube-videos/
    other/
  templates/        blank scene templates — copy one when adding a new source
  docs/
    methodology.md  scene schema, scoring approach, change log
  scoring/          score.py (the ranking algorithm) + atmos-check.csv
                    + timestamps.csv + tv-shows.txt
                    + descriptions.csv + scene-names.csv
  output/           top-100.md + top-100.csv + ranking.csv (auto-generated — do not hand-edit)
```

## Schema (short version)

Each source file is YAML frontmatter with a `scenes_mentioned:` list. Each entry identifies the film, the scene within it (`scene_name` + `normalized_scene_id`), an optional `timestamp`, an optional `rank` (if the source ranks its scenes), and a one-line description. See [docs/methodology.md](docs/methodology.md) for the full schema.

`normalized_scene_id` follows `{normalized_title}--{kebab-case scene name}` and is the join key across sources that describe the same scene differently.

## Status

**Live.** 48 sources captured (24 Reddit posts, 11 blogs, 8 YouTube videos, 5 news articles) covering 400 unique scenes. The ranking covers **feature films only** — 354 scenes rank, after dropping 21 TV-show scenes (out of scope) and 25 scenes from films with no Dolby Atmos home mix. Scoring v1 is implemented in [scoring/score.py](scoring/score.py); the published ranking is [output/top-100.md](output/top-100.md) / [output/top-100.csv](output/top-100.csv), with the full table in [output/ranking.csv](output/ranking.csv). See [docs/methodology.md](docs/methodology.md) for the scoring algorithm and change log.

Regenerate the ranking after adding or editing sources:

```bash
.venv/bin/python scenes/scoring/score.py
```
