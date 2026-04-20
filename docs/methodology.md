# Methodology

> **Status:** v1 scoring algorithm is implemented in [`scoring/score.py`](../scoring/score.py). Outputs land in [`output/top-100.md`](../output/top-100.md) and [`output/ranking.csv`](../output/ranking.csv). Re-run the script any time new sources are added.

## Scoring algorithm (v1)

For every movie mention in every source file:

```
score_per_mention = tier_multiplier × rank_multiplier × engagement_multiplier
```

Then the **aggregate score per film** is the sum of that across all mentions of the same `normalized_title`.

### Tier multiplier — articles only

Applied to blog and news sources. Reddit and YouTube pin this to `1.0` (they're weighted by engagement instead).

| Tier | Weight |
|---|---|
| `top` | 3.0 |
| `high` | 2.0 |
| `mid` | 1.0 |
| `low` | 0.25 |

Tier assignments live in [source-authority-tiers.md](source-authority-tiers.md).

### Rank multiplier — ranked lists only

Applied when `is_ranked_list: true`. Defaults to `1.0` otherwise.

```
rank_multiplier = 1 + ((list_length - rank + 1) / list_length) × 0.5
```

Max 1.5× for rank 1, ~1.05× for the last entry. Intentionally modest — being #1 of 10 is a stronger signal than being #10, but not dominantly so.

### Engagement multiplier — per source type

- **Articles** (blog, news): `1.0` (no engagement adjustment; already weighted by tier)
- **Reddit post — OP body**: `sqrt(post_upvotes)`
- **Reddit post — comment**: `sqrt(comment_upvotes)`
- **Reddit comment** (standalone file): `sqrt(comment_upvotes)`
- **YouTube**: `sqrt(video_views + channel_subscribers / 10) / 50`

Square-root scaling was chosen deliberately: linear lets one viral comment crush the dataset, log scaling is so flat it ignores genuine upvote signal, sqrt is the middle ground that respects community validation without collapsing the ranking onto any single voice.

The `/ 50` normalizer on YouTube brings big-channel videos into a range comparable to article tiers and Reddit upvote weights — without it, a single 100K-view YouTube video would outweigh the combined signal from all article sources.

### Tie-breaking

Identical scores sort by: mention count (desc), then normalized_title (asc).

### Deferred for v1

- **Recency decay** — older sources weighted the same as newer ones. Layer in later if useful.
- **Sentiment** — the schema doesn't capture sentiment, so every mention is treated as positive. Fine in practice: contributors almost exclusively post positive recommendations; explicit negative mentions are filtered out during source capture (see `CHANGE LOG` below).
- **Community phase bonus** — a reserved scoring bucket for after the draft list is posted to the project's subreddit.

## Atmos availability verification

Because sources frequently recommend films that don't actually have a Dolby Atmos mix — viewers enjoy the audio and lump it in, even when the home release is 5.1 only — every candidate for the final top 100 is cross-checked for Atmos availability before publishing.

Films that sources recommend but that lack an Atmos home release are listed in [`scoring/excluded.txt`](../scoring/excluded.txt) with a short rationale per entry. Those mentions stay in the source files (data fidelity is preserved) but don't contribute to scoring.

Verification uses authoritative sources: HighDefDigest and AVForums for 4K Blu-ray audio-track specs, Dolby's own Atmos listings for streaming availability, and Blu-ray.com for edition-specific audio details. When a commenter in the captured sources points out a film isn't actually in Atmos (e.g. Nolan films, Prometheus), that cross-corroboration also counts.

## Goal

Produce a transparent, reproducible top-100 ranking of the best Dolby Atmos movies by aggregating many public sources (blog articles, news articles, Reddit posts, Reddit comments, and more), then layer community input from the project's subreddit on top.

## Principles

1. **Every source is linked back to its original.** Each source file records the canonical URL so any reader can follow it to the original article, post, or comment.
2. **Structured metadata is added by hand.** A human reads each source and records every movie it recommends, plus rank position if the source is a ranked list. Explicit non-Atmos mentions and negative/critical mentions are filtered out at capture time.
3. **The algorithm is auditable.** Every score a movie receives can be traced back to the specific source files and mentions that contributed to it. Grep the repo for any `normalized_title` to see all mentions feeding its score.
4. **Nothing is hidden.** Source authority tier assignments, algorithm weights, and any changes to the scoring are committed to this repo with explanations.

## Candidate scoring factors (to be calibrated)

The factors below are on the table. Weights and exact formulas will be decided once we can see the real data — there's no point picking a logarithmic scaling constant for Reddit upvotes before we know whether typical mentions sit at 5 upvotes or 500.

### Always on (planned)

- **Base mention** — every mention of a movie in a source contributes at least some points. Floor: a single point.
- **Rank position in ranked lists** — being #1 on a "Top 10" list should weigh more than being #10. The exact decay curve (linear, log, 1/rank) is TBD. Must normalize for list length — #5 of 10 is not the same signal as #5 of 100.

### Under consideration (priority)

- **Source authority tier** — outlets like IGN, What Hi-Fi, Dolby's own reference lists, and well-known home-theater publications should weigh more than small personal blogs. Tiers tracked in [source-authority-tiers.md](source-authority-tiers.md). Tier weights TBD.
- **Reddit upvote scaling** — a comment with 500 upvotes carries more signal than one with 3, but the relationship is almost certainly non-linear (log or square-root). Will calibrate once we see the upvote distribution across collected sources.
- **YouTube engagement scaling** — videos carry signal based on channel subscribers and view count. Like Reddit, the relationship is almost certainly non-linear. A list on a 2M-subscriber AV channel with 500K views should weigh more than a 300-view video on a 1K-subscriber channel. Calibrate once data distribution is clearer.

### Under consideration (lower priority, pending data)

- **Recency decay** — the Atmos catalog grows quickly and mixing standards change. Older "best of" lists may deserve lower weight. Needs a defensible half-life.
- **Community phase bonus** — reserved scoring bucket applied after the draft list is posted to the project's subreddit. Exact mechanic TBD; likely a structured upvote/comment poll rather than freeform text mining.

## Open questions

- How do we handle a movie that appears in a ranked list once and in 20 unranked passing mentions? Is one strong rank signal worth more than many weak mentions?
- How do we deduplicate movies across sources? Planned: `normalized_title` field (lowercase, hyphenated, no punctuation) + manual review. Year disambiguates remakes.
- Do we score theatrical Atmos mixes and home-release Atmos mixes separately? Different sources sometimes mean different things.
- How do we prevent a single viral Reddit thread from dominating? Likely a per-source-file cap on how many points any one movie can earn.

## Change log

Every change to the scoring algorithm or tier assignments is recorded here.

- **2026-04-18** — v1 algorithm implemented. Tier weights `top=3.0/high=2.0/mid=1.0/low=0.25`, rank bonus max 1.5× for #1, sqrt engagement scaling for Reddit, `sqrt(views + subs/10) / 50` for YouTube. See `scoring/score.py`.
- **2026-04-18** — Tier assignments made for sources 001–016. 3 top, 6 high, 3 mid, 4 low. See [source-authority-tiers.md](source-authority-tiers.md).
- **2026-04-19** — Exclusion list added (`scoring/excluded.txt`). First exclusion: Interstellar (Nolan, 5.1 only). Script modified to load the list and skip excluded titles from the ranking while keeping them in the source data.
- **2026-04-19** — Exclusions extended to cover all Nolan films in the pool (Interstellar, Oppenheimer, Tenet, Dunkirk) plus Arrival, Prometheus, Super 8, and Terminator 2 as non-Atmos films that viewers repeatedly recommended.
- **2026-04-20** — Full sanity sweep of the top 100 for Atmos availability (see subsection above). Only Inception needed to be added; all other uncertain films (Brave, WALL·E, War of the Worlds 2005, The Amazing Spider-Man 2012, Star Wars saga) verified via HighDefDigest/Dolby/Blu-ray.com to have Atmos home releases. Exclusion list now stands at 9 films.
- **2026-04-20** — Heat (1995) added to exclusions after targeted verification. The 2022 Director's Definitive Edition 4K UHD ships with DTS-HD MA 5.1 only, no Atmos track. This was a miss in the earlier sanity sweep — I had assumed the 4K remaster added Atmos. Lesson for the verification process: don't assume 4K remasters automatically add Atmos; confirm per-film against HighDefDigest or Blu-ray.com.
