"""Aggregate TV-show mentions across all sources and produce the ranked Top 50 shows.

Algorithm (v1) — see docs/methodology.md for the full rationale. Forked from
the scenes-side engine (../../scenes/scoring/score.py); same formula, but the
ranked unit is a whole series aggregated on `normalized_title`.

    per-mention score = tier x rank x engagement
    raw_score         = sum of per-mention scores for a show
    final_score       = raw_score x breadth_multiplier

Tier (articles only):   top=3.0  high=2.0  mid=1.0  low=0.25  unknown=0.25
                        Reddit / YouTube / forums are never tier-weighted (tier = 1.0).
Rank (ranked lists):    1 + ((list_length - rank + 1) / list_length) x 0.5
Engagement
  - articles:           1.0  (weighted by tier instead)
  - Reddit:             1 + ln(upvotes) / REDDIT_K
  - YouTube:            1 + ln(max(views + subs/10, YT_BASE) / YT_BASE) / YT_K
  - forum-post:         1.0  (no upvote system; every voice at the floor)
Breadth:                1 + BREADTH_B x ln(num_sources)

`num_sources` is the count of distinct source files (threads + articles +
videos) that mention the show, so a show corroborated across many independent
sources outranks one a single popular thread happens to love.

Shows verified to have no Dolby Atmos mix anywhere are dropped by joining
`normalized_title` against scoring/excluded.txt (this list's own file — NOT
the movie-side one). Verification happens externally; scoring/atmos-check.csv
is the handoff worksheet, emitted fresh on every run with curator-entered
columns preserved.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent              # tv-shows/
SOURCES_DIR = ROOT / "sources"
OUTPUT_DIR = ROOT / "output"
EXCLUSIONS_FILE = Path(__file__).resolve().parent / "excluded.txt"      # own list, not the movie-side one
ATMOS_CHECK_FILE = Path(__file__).resolve().parent / "atmos-check.csv"  # verification worksheet
DESCRIPTIONS_FILE = Path(__file__).resolve().parent / "descriptions.csv"  # optional cleaned copy

TOP_N = 50

# Tier weights. `unknown` deliberately equals `low`: an un-vetted source is
# treated cautiously, not given neutral (mid) credit, until it is assessed.
TIER_WEIGHTS = {"top": 3.0, "high": 2.0, "mid": 1.0, "low": 0.25, "unknown": 0.25}

# Tunable curve constants (see methodology.md).
REDDIT_K = 4.0      # Reddit engagement:  1 + ln(upvotes) / REDDIT_K
YT_K = 4.0          # YouTube engagement: 1 + ln(reach / YT_BASE) / YT_K
YT_BASE = 3000.0    # YouTube reach baseline; reach = video_views + subs/10
BREADTH_B = 0.5     # breadth multiplier: 1 + BREADTH_B * ln(num_sources)


def load_title_list(path: Path) -> set:
    """Load a list of normalized_titles (one per line; # comments ignored)."""
    if not path.exists():
        return set()
    titles = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            titles.add(line)
    return titles


def load_description_overrides() -> dict:
    """Editor-cleaned show descriptions for the published output.

    A show's description otherwise comes verbatim from the longest captured
    source mention. descriptions.csv supplies copy-edited versions for the
    published-facing CSVs, without altering what the sources actually wrote.
    """
    overrides = {}
    if DESCRIPTIONS_FILE.exists():
        with DESCRIPTIONS_FILE.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                nt = (row.get("normalized_title") or "").strip()
                desc = (row.get("description") or "").strip()
                if nt and desc:
                    overrides[nt] = desc
    return overrides


def load_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[3:end])


def tier_multiplier(source) -> float:
    if source["source_type"] in ("blog", "news"):
        tier = source.get("authority_tier") or "unknown"
        return TIER_WEIGHTS.get(tier, TIER_WEIGHTS["unknown"])
    return 1.0


def rank_multiplier(source, mention) -> float:
    if not source.get("is_ranked_list"):
        return 1.0
    rank = mention.get("rank")
    length = source.get("list_length")
    if rank is None or not length:
        return 1.0
    return 1.0 + ((length - rank + 1) / length) * 0.5


def engagement_multiplier(source, mention) -> float:
    st = source["source_type"]
    if st in ("blog", "news"):
        return 1.0
    if st == "reddit-post":
        if mention.get("mentioned_by") == "OP" and mention.get("comment_upvotes") is None:
            upvotes = source.get("post_upvotes") or 1
        else:
            upvotes = mention.get("comment_upvotes") or 1
        return 1.0 + math.log(max(upvotes, 1)) / REDDIT_K
    if st == "reddit-comment":
        upvotes = source.get("comment_upvotes") or 1
        return 1.0 + math.log(max(upvotes, 1)) / REDDIT_K
    if st == "youtube":
        reach = (source.get("video_views") or 0) + (source.get("channel_subscribers") or 0) / 10
        return 1.0 + math.log(max(reach, YT_BASE) / YT_BASE) / YT_K
    return 1.0  # forum-post and anything else: flat community voice


def score_mention(source, mention) -> float:
    return (
        tier_multiplier(source)
        * rank_multiplier(source, mention)
        * engagement_multiplier(source, mention)
    )


def load_sources():
    sources = []
    for path in sorted(SOURCES_DIR.glob("**/*.md")):
        if path.name == ".gitkeep":
            continue
        fm = load_frontmatter(path)
        if fm is None:
            print(f"  skipped (no frontmatter): {path.relative_to(ROOT)}")
            continue
        fm["_key"] = str(path.relative_to(SOURCES_DIR))  # stable, unique per file
        sources.append(fm)
    return sources


def aggregate(sources):
    shows = defaultdict(
        lambda: {
            "title_counts": defaultdict(int),      # show_title spellings
            "year_counts": defaultdict(int),       # first_air_year
            "platform_counts": defaultdict(int),
            "descriptions": [],
            "raw": 0.0,
            "mentions": 0,
            "sources": set(),
        }
    )
    for source in sources:
        for mention in source.get("shows_mentioned") or []:
            nt = mention.get("normalized_title")
            if not nt:
                continue
            data = shows[nt]
            data["raw"] += score_mention(source, mention)
            data["mentions"] += 1
            data["sources"].add(source["_key"])
            if title := mention.get("show_title"):
                data["title_counts"][title] += 1
            if year := mention.get("first_air_year"):
                data["year_counts"][str(year)] += 1
            if platform := mention.get("platform"):
                data["platform_counts"][platform] += 1
            if desc := mention.get("description"):
                data["descriptions"].append(desc.strip())
    for data in shows.values():
        data["score"] = data["raw"] * (1.0 + BREADTH_B * math.log(len(data["sources"])))
    return shows


def _most_common(counts, fallback="", tie_key=lambda kv: -len(kv[0])):
    """Most frequent key; ties broken by tie_key (default: shorter string)."""
    if not counts:
        return fallback
    return max(counts.items(), key=lambda kv: (kv[1], tie_key(kv)))[0]


def canonical_title(data, fallback):
    return _most_common(data["title_counts"], fallback)


def canonical_year(data):
    # most common year wins; ties broken on earliest
    return _most_common(data["year_counts"], "", tie_key=lambda kv: -int(kv[0]))


def canonical_platform(data):
    return _most_common(data["platform_counts"], "")


def canonical_description(data):
    # the longest description across the show's mentions — usually the most
    # informative; sources write one-liners so length is a fair proxy.
    return max(data["descriptions"], key=len) if data["descriptions"] else ""


def write_csv(ranked, path, descriptions, limit=None):
    rows = ranked[:limit] if limit else ranked
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "rank",
                "show_title",
                "first_air_year",
                "normalized_title",
                "platform",
                "score",
                "mentions",
                "num_sources",
                "description",
            ]
        )
        for i, (nt, data) in enumerate(rows, 1):
            writer.writerow(
                [
                    i,
                    canonical_title(data, nt),
                    canonical_year(data),
                    nt,
                    canonical_platform(data),
                    f"{data['score']:.3f}",
                    data["mentions"],
                    len(data["sources"]),
                    descriptions.get(nt) or canonical_description(data),
                ]
            )


def write_markdown(ranked, path, top_n=TOP_N, excluded=None):
    lines = [
        f"# Top {top_n} Dolby Atmos TV Shows",
        "",
        f"*Auto-generated by [`scoring/score.py`](../scoring/score.py) from "
        f"{len(ranked)} ranked shows across all sources. Do not hand-edit.*",
        "",
        "See [docs/methodology.md](../docs/methodology.md) for how scores are calculated.",
        "",
        "*Provisional — Atmos availability verification is in progress; shows may be "
        "removed once verified (see [`../scoring/excluded.txt`](../scoring/excluded.txt) "
        "and [`../scoring/atmos-check.csv`](../scoring/atmos-check.csv)).*",
        "",
    ]
    if excluded:
        lines.append(
            f"*{len(excluded)} show(s) captured in sources were excluded from this "
            f"ranking because no Dolby Atmos mix could be verified. "
            f"See [`../scoring/excluded.txt`](../scoring/excluded.txt).*"
        )
        lines.append("")
    lines += [
        "| Rank | Show | Year | Platform | Score | Mentions | Sources |",
        "|---:|---|---:|---|---:|---:|---:|",
    ]
    for i, (nt, data) in enumerate(ranked[:top_n], 1):
        lines.append(
            f"| {i} | {canonical_title(data, nt)} | {canonical_year(data) or '—'} | "
            f"{canonical_platform(data) or '—'} | {data['score']:.2f} | "
            f"{data['mentions']} | {len(data['sources'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_atmos_check(shows):
    """Emit/refresh the verification worksheet, preserving curator entries.

    One row per captured show (pre-exclusion). `is_atmos` and `notes` are
    curator-owned and always preserved; `platform` keeps the curator's value if
    set, else the canonical (most common) captured platform. Shows no longer
    captured are dropped; new shows appended with is_atmos empty.
    """
    existing = {}
    if ATMOS_CHECK_FILE.exists():
        with ATMOS_CHECK_FILE.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                nt = (row.get("normalized_title") or "").strip()
                if nt:
                    existing[nt] = row
    with ATMOS_CHECK_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["normalized_title", "show_title", "first_air_year", "platform", "is_atmos", "notes"]
        )
        for nt in sorted(shows):
            data = shows[nt]
            prev = existing.get(nt, {})
            writer.writerow(
                [
                    nt,
                    canonical_title(data, nt),
                    canonical_year(data),
                    (prev.get("platform") or "").strip() or canonical_platform(data),
                    (prev.get("is_atmos") or "").strip(),
                    (prev.get("notes") or "").strip(),
                ]
            )


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    sources = load_sources()
    shows = aggregate(sources)

    # Refresh the verification worksheet from the PRE-exclusion aggregate, so
    # the curator always sees every captured show.
    write_atmos_check(shows)

    # Drop shows verified to have no Atmos mix (join on normalized_title).
    exclusions = load_title_list(EXCLUSIONS_FILE)
    unmatched = exclusions - set(shows)
    for nt in sorted(unmatched):
        print(f"  WARNING: excluded.txt entry matches no captured show: {nt}")
    excluded_hits = {nt: shows[nt] for nt in exclusions & set(shows)}
    for nt in excluded_hits:
        del shows[nt]

    ranked = sorted(
        shows.items(),
        # primary: score desc; tie-break on mention count desc, then slug asc
        key=lambda kv: (-kv[1]["score"], -kv[1]["mentions"], kv[0]),
    )

    descriptions = load_description_overrides()
    csv_path = OUTPUT_DIR / "ranking.csv"
    top_csv_path = OUTPUT_DIR / f"top-{TOP_N}.csv"
    md_path = OUTPUT_DIR / f"top-{TOP_N}.md"
    write_csv(ranked, csv_path, descriptions)
    write_csv(ranked, top_csv_path, descriptions, limit=TOP_N)
    write_markdown(ranked, md_path, top_n=TOP_N, excluded=excluded_hits)

    print(f"Scored {len(shows)} distinct shows across {len(sources)} sources.")
    if excluded_hits:
        print(f"Excluded {len(excluded_hits)} show(s) (no verified Atmos mix, see scoring/excluded.txt).")
    print(f"  Full CSV:  {csv_path.relative_to(ROOT)}")
    print(f"  Top {TOP_N}:    {top_csv_path.relative_to(ROOT)} / {md_path.relative_to(ROOT)}")
    print(f"  Worksheet: {ATMOS_CHECK_FILE.relative_to(ROOT)}")
    print()
    print("Top 25 preview:")
    for i, (nt, data) in enumerate(ranked[:25], 1):
        print(
            f"  {i:>3}. {canonical_title(data, nt)}  "
            f"score={data['score']:.2f}  mentions={data['mentions']}  "
            f"sources={len(data['sources'])}"
        )


if __name__ == "__main__":
    main()
