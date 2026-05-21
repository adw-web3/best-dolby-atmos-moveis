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
  scoring/          (empty for now; algorithm will be added once enough sources exist)
  output/           (empty for now; ranking will be auto-generated)
```

## Schema (short version)

Each source file is YAML frontmatter with a `scenes_mentioned:` list. Each entry identifies the film, the scene within it (`scene_name` + `normalized_scene_id`), an optional `timestamp`, an optional `rank` (if the source ranks its scenes), and a one-line description. See [docs/methodology.md](docs/methodology.md) for the full schema.

`normalized_scene_id` follows `{normalized_title}--{kebab-case scene name}` and is the join key across sources that describe the same scene differently.

## Status

**Scaffolding complete.** Templates and methodology in place; no sources captured yet. Backfill of the four scene-focused articles already in the movie-side `sources/` ([001](../sources/news-articles/001-whathifi-best-dolby-atmos-movie-scenes.md), [003](../sources/blog-articles/003-audioadvice-top-10-dolby-atmos-movie-scenes.md), [006](../sources/news-articles/006-hifi-de-15-filmszenen-dolby-atmos.md), [009](../sources/blog-articles/009-audioadvice-best-dolby-atmos-movie-scenes.md)) is the next step.
