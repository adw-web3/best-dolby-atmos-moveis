# Methodology — TV show ranking

> **Status:** scaffolded. Schema and capture workflow are defined below; scoring is designed (fork of the scenes v2 engine) but not yet implemented — it lands once sources are captured. The published ranking will live at `../output/top-50.md` with the full table in `../output/ranking.csv`.

This sub-project ranks **TV series with Dolby Atmos mixes** (e.g. "Stranger Things", "Our Planet"), as recommended across home-theater publications, blogs, Reddit threads, and YouTube. It is fully separated from the movie ranking under [`../../sources/`](../../sources/) and the scene ranking under [`../../scenes/sources/`](../../scenes/sources/) — sources collected here are only used for the TV ranking. The same article may legitimately appear in more than one place, captured once per ranking it feeds.

## Show-source schema

Each source file is YAML frontmatter. Source-type-specific fields (subreddit/upvotes, channel/views, etc.) mirror the movie- and scene-side templates so the scoring engine can reuse the same engagement math.

The primary unit is a **series**, not an episode or season. Mentions of a specific episode or season roll up to the show; what was cited is preserved in `episode_ref`.

```yaml
shows_mentioned:
  - show_title: "Stranger Things"
    first_air_year: 2016
    normalized_title: "stranger-things"   # aggregation key — series-level slug
    platform: "Netflix"                    # only if the source states it; null otherwise
    episode_ref: "S4E6"                    # what the source actually cited; null if series-wide praise
    rank: 3                                # null if the source doesn't rank its picks
    description: "Running Up That Hill sequence praised for overhead activity and bass."
```

### `normalized_title` convention

Series name in kebab-case (`stranger-things`, `game-of-thrones`, `our-planet`), lowercase, no punctuation. A year suffix is appended **only when needed to disambiguate** two shows with the same name (e.g. `dark-2017` only if another "Dark" enters the pool), matching the movie-side convention.

Mapping from the scenes-side episode slugs: `stranger-things-s4e6` (scenes) → show `stranger-things` here, with `episode_ref: "S4E6"`.

### One-entry-per-show-per-voice rule

A single voice (one commenter, one list item, one article section) citing multiple episodes or seasons of the same show is captured as **one** `shows_mentioned` entry — episodes concatenated in `episode_ref` (e.g. `"S1E1; S4E6"`), and if a ranked list places two episodes of one show at different positions, the **best** rank is kept. Otherwise one enthusiastic voice double-counts a show.

Distinct voices (different commenters, different articles) mentioning the same show remain distinct mentions — that cross-voice consensus is exactly the signal being measured.

### Vague-mention rule (inverted vs scenes)

Because the ranked unit is the whole series, **series-level praise counts**. "All of Andor sounds incredible" is a valid mention here (`episode_ref: null`) — the same sentence would be a skip on the scenes side. Any identifiable show reference counts; only mentions that can't be tied to a specific series are skipped.

### Scope: TV series with an Atmos mix

**In scope:**

- Scripted series (drama, comedy, animation).
- Miniseries / limited series (e.g. *Midnight Mass*, *Masters of the Air*, *The Fall of the House of Usher*).
- Documentary and nature series (e.g. *Our Planet*, *The Green Planet*, *Planet Earth II*) — prime Atmos TV content, deliberately included.

**Out of scope:**

- **Films of any kind** — theatrical or made-for-TV; that's the [movie ranking's](../../README.md) job.
- Standalone concert recordings / specials and music videos (same rule as the scenes ranking).
- One-off TV specials that aren't part of a series; live sports and event broadcasts.
- Atmos demo discs and test clips.
- Video games — including games adapted from or into in-scope shows (e.g. *The Witcher 3*'s Atmos mode is not signal for *The Witcher* the series).
- **Picks where a source explicitly flags the show as not Atmos** (e.g. "5.1 only on disc, no Atmos anywhere").

For shows whose Atmos status isn't called out, capture normally — scoring filters via `../scoring/excluded.txt` after verification (see below).

### Same-publication-snapshot rule

Reused verbatim from the scenes ranking: a single editorial voice making the same picks counts as **one** source. Skip a continuously-updated article's older snapshots (capture only the most recent version), and skip a creator's second medium when the picks are identical (blog post vs YouTube video — capture one, prefer better engagement metadata or the first published). Distinct articles from the same publication with different authors or substantively different picks remain independent sources.

## Authority tiers

The shared [`../../docs/source-authority-tiers.md`](../../docs/source-authority-tiers.md) applies to TV sources too — a publication that's `top` for the movie ranking is `top` here. New outlets encountered during capture get appended there. As on the scenes side, an **`unknown` (un-assessed) source is weighted as `low`**, not neutral `mid`.

## Scoring (planned — fork of the scenes v2 engine)

The scenes-side engine ([`../../scenes/scoring/score.py`](../../scenes/scoring/score.py)) is the fork base; its v1 formula and constants carry over unchanged. The aggregation key is `normalized_title`.

```
per-mention score = tier × rank × engagement
raw_score         = Σ per-mention scores for a show
final_score       = raw_score × (1 + 0.5 × ln(num_sources))
```

**Tier** (articles only — Reddit/YouTube are never tier-weighted): `top` ×3, `high` ×2, `mid` ×1, `low` ×0.25, `unknown` ×0.25.

**Rank** (ranked lists only): `1 + ((list_length − rank + 1) / list_length) × 0.5` — up to +50% for the top pick.

**Engagement** — articles ×1 (carried by tier instead); Reddit `1 + ln(upvotes)/4`; YouTube `1 + ln(reach/3000)/4` where `reach = video_views + channel_subscribers/10`. Bounded `ln` curves, so no single viral comment or video outranks vetted editorial coverage.

**Breadth** — `× (1 + 0.5 × ln(num_sources))`, rewarding cross-source consensus with diminishing returns.

TV-side differences from the scenes engine:

- Aggregates `shows_mentioned[]` on `normalized_title` (series-level); no scene/timestamp machinery.
- **Own exclusion list** at `../scoring/excluded.txt` — not the movie-side one, which is film-specific.
- Publishes a **Top 50** (`../output/top-50.md` / `top-50.csv`), not a Top 100 — the pool of series with genuinely praised Atmos mixes is far smaller than for films. Full table in `../output/ranking.csv`.
- Emits `../scoring/atmos-check.csv` on every run (see below).

Output columns: `rank, show_title, first_air_year, normalized_title, platform, score, mentions, num_sources, description`. Canonical values per show are the most common across mentions (`show_title`, `first_air_year` — ties toward earliest, `platform`); `description` is the longest captured mention, overridable via an optional `descriptions.csv`.

## Atmos verification (external handoff)

TV Atmos availability is platform-dependent (a show can be Atmos on Apple TV+ but 5.1 on disc; Netflix requires the Premium tier). Criterion: a show counts as Atmos if **at least one mainstream streaming platform or home-video release ships an Atmos mix**.

Verification is performed **outside this repo** (curator's separate verification project). The loop:

1. `score.py` emits/refreshes [`../scoring/atmos-check.csv`](../scoring/atmos-check.csv) — one row per captured show (`normalized_title, show_title, first_air_year, platform, is_atmos, notes`), pre-exclusion. The write is merge-preserving: rows already filled in are never clobbered; new shows are appended with `is_atmos` blank; shows no longer captured are dropped.
2. The curator verifies each show externally and fills `is_atmos` / `platform` / `notes`.
3. Shows verified non-Atmos are appended to [`../scoring/excluded.txt`](../scoring/excluded.txt) (one `normalized_title` per line, with a comment explaining why); re-running `score.py` drops them from the ranking. The worksheet documents; `excluded.txt` enforces.

Until the round-trip completes, the ranking is provisional and the published output says so.

## Relationship to the other rankings

- **Independent outputs.** The TV ranking does not feed into, and is not derived from, the movie or scene rankings.
- **Shared authority tiers.** Tier assignments in [`../../docs/source-authority-tiers.md`](../../docs/source-authority-tiers.md) apply to all three.
- **Intentional source dupes.** A source covering movies, scenes, and shows may be captured up to three times — once per ranking, each capture holding only the mentions relevant to that ranking's unit.

## Change log

Every change to the TV-side schema or scoring is recorded here.

- **2026-07-22** — External Atmos verification applied. The curator's verification tool checked every captured show; 8 confirmed non-Atmos (The Expanse, Band of Brothers, Black Summer, Better Call Saul, Breaking Bad, Then You Run, Creature, Welcome to Earth) and 1 unverified (Star Wars Rebels) added to [`../scoring/excluded.txt`](../scoring/excluded.txt) with per-entry evidence; verdicts and citations recorded in [`../scoring/atmos-check.csv`](../scoring/atmos-check.csv). Ranking went from 67 → 58 shows. A late 30th source (r/westworld, 1.7K-upvote 4K-disc thread) was captured the same day.
- **2026-07-22** — Capture phase closed at 29 sources / 67 shows (24 Reddit threads across 10 subreddits, 5 news articles, 2 blog articles, 4 forum threads, 1 seed list; no YouTube sources materialized). Scoring v1 implemented and run; provisional ranking published to `../output/`. Verification pipeline exercised end-to-end: worksheet merge-preservation, exclusion round-trip, and slug-typo warning all confirmed. Scoring constants remain subject to a curator review before the ranking is declared final — one open question is documented below (2026-07-22, single-mention band).
- **2026-07-22** — Open scoring question, parked for curator review: eleven shows rank on a single `top`-tier article mention (×3.0) above multi-source community picks; several of those mentions are list-inclusion only, with no audio commentary (marked as such in their descriptions, all from source 014). Candidate remedies: a minimum-2-sources gate for the published top-50, dampening inclusion-only mentions, or accepting the behavior. Same family of question applies to bare-affirmation pile-on comments (source 026).
- **2026-07-22** — Capture phase originally closed at 20 sources / 66 shows before nine late sources were added the same day. New source type `seed-list` (source 020): the TV shows that surfaced during the scenes-ranking capture and were parked out-of-scope in [`../../scenes/scoring/tv-shows.txt`](../../scenes/scoring/tv-shows.txt) are captured as one flat mention per show (engagement ×1.0, like a forum voice) — the underlying per-thread voices were captured for the scene unit and live in `scenes/sources/`. Episode slugs preserved in `episode_ref`; scenes slug `star-wars-andor` maps to `andor`.
- **2026-07-21** — New source type `forum-post` introduced (first capture: a Blu-ray.com forum thread, source 001, filed under `sources/other/`). Structurally like a Reddit thread (OP + commenter voices, `mentioned_by` per mention) but with no upvote system, so scoring will treat every voice at flat ×1.0 engagement — the same floor as a 1-upvote Reddit comment. Forum-specific fields: `forum_section`, `post_num_replies`; forums with a reaction system (e.g. AVForums, source 003) record per-mention `reactions` for fidelity, though scoring stays flat.
- **2026-07-21** — Sub-project scaffolded. Templates, schema, scope rules, and methodology created. Decisions locked: ranked unit is the whole series (episode/season mentions roll up via `episode_ref`); documentary/nature series in scope; Top 50 output; scoring forks the scenes v2 engine unchanged; own `excluded.txt`; Atmos verification handled externally via a script-emitted, merge-preserving `atmos-check.csv`. No sources captured yet; no scoring code yet.
