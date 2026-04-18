# Best Dolby Atmos Movies — a transparent community ranking

This repository is the open, auditable data and methodology behind a crowd-sourced **Top 100 Dolby Atmos Movies** list.

The goal is simple: take every credible recommendation out there — from home-theater publications, tech blogs, news outlets, Reddit threads, and more — structure it, score it with a defensible algorithm, and publish the result so anyone can verify how it was made.

## How this works

1. **Collect sources.** Every article, Reddit post, and Reddit comment that recommends Atmos movies gets added to this repo as a structured Markdown file. The full original text is preserved verbatim so you can always check the data against the source.
2. **Extract mentions.** Each source file lists every movie mentioned, with a short quote, the sentiment, and (if the source is a ranked list) the position.
3. **Score.** A scoring algorithm aggregates mentions across all sources to produce a single ranked list. The algorithm is being designed openly — see [docs/methodology.md](docs/methodology.md).
4. **Community input.** Once a draft list exists, it will be posted to the project's subreddit. Community votes and comments feed back into the scoring as a dedicated bucket before the final Top 100 is published.

## Current status

**Phase 1 — data collection.** We are actively gathering source material. The scoring algorithm is still being designed; see the methodology doc for the open questions.

## Repository layout

```
sources/                     raw structured data, one file per source
  blog-articles/
  news-articles/
  reddit-posts/
  reddit-comments/
  other/
templates/                   blank templates — copy one when adding a new source
docs/
  methodology.md             the scoring algorithm design (work in progress)
  source-authority-tiers.md  how each source is rated, and why
  sources-index.md           running index of every source added
```

## How to read a source file

Every source file has two parts:

- **YAML frontmatter** at the top with structured metadata: source name, URL, date, author, authority tier, and a `movies_mentioned` list with one entry per movie the source recommends (title, year, rank if ranked, sentiment, quote).
- **Raw source text** below the frontmatter: the original article body, post, or comment pasted verbatim so you can verify the structured data against what the source actually said.

## How to verify

- Pick any movie in the final ranking. Grep this repo for its `normalized_title` — every source file that contributed to its score will show up.
- Open those files, read the raw source text at the bottom, and confirm the structured mention matches.
- Every change to the scoring algorithm or to any source's authority tier is committed with an explanation; `git log` is the audit trail.

## How to contribute (once the draft is out)

The community input phase will run on the project's subreddit. Details will be posted here when the draft list is published.

## License

*(TBD)*
