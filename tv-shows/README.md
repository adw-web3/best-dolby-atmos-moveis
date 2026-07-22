# Best Dolby Atmos TV Shows

Parallel sub-project of the [best Dolby Atmos movies ranking](../README.md), alongside the [demo scenes ranking](../scenes/README.md). Same data-driven, auditable approach — but the ranked unit here is a **whole series** (e.g. "Stranger Things"), including miniseries and documentary/nature series.

## How it relates to the other rankings

- **Independent output.** The TV ranking is generated separately and does not influence the movie top-100 or the scenes top-100.
- **Separate sources.** Articles, posts, and videos captured under [`sources/`](sources/) are used only for the TV ranking. A source that covers movies *and* shows will be captured both here (for its show picks) and in the movie-side [`../sources/`](../sources/) (for its film mentions). The duplication is intentional — different rankings, different units, same source.
- **Shared authority tiers.** [`../docs/source-authority-tiers.md`](../docs/source-authority-tiers.md) applies to all three sub-projects.
- **Seeded by the scenes work.** TV shows kept surfacing during scene capture and were parked in [`../scenes/scoring/tv-shows.txt`](../scenes/scoring/tv-shows.txt) (out of scope there); those ~13 shows are the known-recommended baseline this list must at minimum cover.

## Layout

```
tv-shows/
  sources/          raw structured data, one file per source
    blog-articles/
    news-articles/
    reddit-posts/
    reddit-comments/
    youtube-videos/
    other/
  templates/        blank templates — copy one when adding a new source
  docs/
    methodology.md  show schema, scope rules, scoring approach, change log
  scoring/          score.py (the ranking algorithm) + excluded.txt + atmos-check.csv
  output/           top-50.md + top-50.csv + ranking.csv (auto-generated — do not hand-edit)
```

## Schema (short version)

Each source file is YAML frontmatter with a `shows_mentioned:` list. Each entry identifies the series (`show_title` + `normalized_title`, the aggregation key), an optional `platform`, an optional `episode_ref` recording which episode/season the source cited (metadata only — mentions always roll up to the show), an optional `rank`, and a one-line description. See [docs/methodology.md](docs/methodology.md) for the full schema.

## Status

**Ranking published — Atmos-verified.** 30 sources captured (25 Reddit threads, 5 news articles, 2 blog articles, 4 forum threads, plus the scenes-side seed list) covering 67 unique shows, of which **58 rank** after external Atmos verification excluded 9 (8 confirmed non-Atmos, 1 unverifiable — see [scoring/excluded.txt](scoring/excluded.txt) and the evidence notes in [scoring/atmos-check.csv](scoring/atmos-check.csv)). Scoring v1 is implemented in [scoring/score.py](scoring/score.py); the ranking is [output/top-50.md](output/top-50.md) / [output/top-50.csv](output/top-50.csv), with the full table in [output/ranking.csv](output/ranking.csv).

One scoring question remains open for curator review (single-mention article picks — see the [methodology change log](docs/methodology.md)); the ranking is final in all other respects.

Regenerate the ranking after adding or editing sources or exclusions:

```bash
.venv/bin/python tv-shows/scoring/score.py
```
