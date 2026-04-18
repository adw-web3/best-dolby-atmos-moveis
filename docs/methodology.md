# Methodology — work in progress

> **Status:** Data collection phase. The scoring algorithm below is a **live discussion document**, not a final spec. Decisions will be made once enough source data has been gathered to see the real distribution (how ranked lists are structured, what Reddit upvote counts look like, how sources cluster by authority). This doc is the audit trail for how the algorithm evolves.

## Goal

Produce a transparent, reproducible top-100 ranking of the best Dolby Atmos movies by aggregating many public sources (blog articles, news articles, Reddit posts, Reddit comments, and more), then layer community input from the project's subreddit on top.

## Principles

1. **Every source is preserved verbatim.** The raw text of every article, post, and comment is kept in the source file so any reader can verify the structured data against the original.
2. **Structured metadata is added by hand** (for now — a script may assist later). A human reads each source and records every movie mention with a short quote, sentiment, and (if applicable) rank position.
3. **The algorithm is auditable.** Every score a movie receives can be traced back to the specific source files and mentions that contributed to it.
4. **Nothing is hidden.** Source authority tier assignments, algorithm weights, and any changes to the scoring are committed to this repo with explanations.

## Candidate scoring factors (to be calibrated)

The factors below are on the table. Weights and exact formulas will be decided once we can see the real data — there's no point picking a logarithmic scaling constant for Reddit upvotes before we know whether typical mentions sit at 5 upvotes or 500.

### Always on (planned)

- **Base mention** — every mention of a movie in a source contributes at least some points. Floor: a single point.
- **Rank position in ranked lists** — being #1 on a "Top 10" list should weigh more than being #10. The exact decay curve (linear, log, 1/rank) is TBD. Must normalize for list length — #5 of 10 is not the same signal as #5 of 100.

### Under consideration (priority)

- **Source authority tier** — outlets like IGN, What Hi-Fi, Dolby's own reference lists, and well-known home-theater publications should weigh more than small personal blogs. Tiers tracked in [source-authority-tiers.md](source-authority-tiers.md). Tier weights TBD.
- **Reddit upvote scaling** — a comment with 500 upvotes carries more signal than one with 3, but the relationship is almost certainly non-linear (log or square-root). Will calibrate once we see the upvote distribution across collected sources.

### Under consideration (lower priority, pending data)

- **Sentiment** — "demo disc quality" is a different signal from "the Atmos mix is disappointing." Negative/critical mentions may score zero or negative. Needs careful definition so we don't silently penalize legitimate critique.
- **Recency decay** — the Atmos catalog grows quickly and mixing standards change. Older "best of" lists may deserve lower weight. Needs a defensible half-life.
- **Community phase bonus** — reserved scoring bucket applied after the draft list is posted to the project's subreddit. Exact mechanic TBD; likely a structured upvote/comment poll rather than freeform text mining.

## Open questions

- How do we handle a movie that appears in a ranked list once and in 20 unranked passing mentions? Is one strong rank signal worth more than many weak mentions?
- How do we deduplicate movies across sources? Planned: `normalized_title` field (lowercase, hyphenated, no punctuation) + manual review. Year disambiguates remakes.
- Do we score theatrical Atmos mixes and home-release Atmos mixes separately? Different sources sometimes mean different things.
- How do we prevent a single viral Reddit thread from dominating? Likely a per-source-file cap on how many points any one movie can earn.

## Change log

Every change to the scoring algorithm or tier assignments will be recorded here, dated, with a one-line reason. This is the audit trail.

- *(none yet — scoring algorithm not yet defined)*
