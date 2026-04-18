# Best Dolby Atmos Movies: a transparent community ranking

This repository is the open, auditable data and methodology behind a crowd-sourced **Top 100 Dolby Atmos Movies** list.

The goal is simple: take every credible recommendation out there (from home-theater publications, tech blogs, news outlets, Reddit threads, and more), structure it, score it with a defensible algorithm, and publish the result so anyone can verify how it was made.

## How this works

1. **Collect sources.** Every article, Reddit post, and Reddit comment that recommends Atmos movies gets added to this repo as a structured Markdown file. Each file records the source URL so you can always go back to the original.
2. **Extract mentions.** Each source file lists every movie mentioned and (if the source is a ranked list) the rank position.
3. **Score.** A scoring algorithm aggregates mentions across all sources to produce a single ranked list. The algorithm is being designed openly; see [docs/methodology.md](docs/methodology.md).
4. **Community input.** Once a draft list exists, it will be posted to the project's subreddit. Community votes and comments feed back into the scoring as a dedicated bucket before the final Top 100 is published.

## Current status

**Phase 2: draft ranking produced.** 36 sources have been captured (blog articles, news articles, Reddit threads, YouTube videos). The v1 scoring algorithm is live in [scoring/score.py](scoring/score.py) and the current draft ranking is at [output/top-100.md](output/top-100.md). Methodology is in [docs/methodology.md](docs/methodology.md).

## Repository layout

```
sources/                     raw structured data, one file per source
  blog-articles/
  news-articles/
  reddit-posts/
  reddit-comments/
  youtube-videos/
  other/
templates/                   blank templates, copy one when adding a new source
scoring/                     the Python scoring script + its README
output/                      auto-generated ranking (CSV + markdown top 100)
docs/
  methodology.md             the scoring algorithm and rationale
  source-authority-tiers.md  how each source is rated, and why
  sources-index.md           running index of every source added
```

## How to read a source file

Each source file is pure YAML frontmatter with structured metadata: source name, URL, date, author, authority tier, and a `movies_mentioned` list with one entry per movie the source recommends (title, year, normalized title, rank if ranked). To verify a mention against the original, follow the `source_url`.

## How to verify

- Pick any movie in the final ranking. Grep this repo for its `normalized_title` — every source file that contributed to its score will show up.
- Open those files, follow each `source_url` back to the original article/post, and confirm the mention matches.
- Every change to the scoring algorithm or to any source's authority tier is committed with an explanation; `git log` is the audit trail.

## How to contribute (once the draft is out)

The community input phase will run on r/DolbyAtmosContent subreddit. Details will be posted here when the draft list is published.
