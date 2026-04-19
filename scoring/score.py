"""Aggregate mentions across all sources and produce the ranked Top 100.

Algorithm (v1):
    score_per_mention = tier_multiplier × rank_multiplier × engagement_multiplier
    aggregate_score   = sum of mention scores per normalized_title

Tier weights (articles only):  top=3.0, high=2.0, mid=1.0, low=0.25
Rank bonus (ranked lists):     1 + ((list_length - rank + 1) / list_length) × 0.5
Reddit engagement:             sqrt(upvotes)
YouTube engagement:            sqrt(views + subs/10) / 50

See docs/methodology.md for the full rationale.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
OUTPUT_DIR = ROOT / "output"
EXCLUSIONS_FILE = ROOT / "scoring" / "excluded.txt"

TIER_WEIGHTS = {"top": 3.0, "high": 2.0, "mid": 1.0, "low": 0.25, "unknown": 1.0}
YOUTUBE_NORMALIZER = 50.0


def load_exclusions() -> set[str]:
    if not EXCLUSIONS_FILE.exists():
        return set()
    exclusions = set()
    for line in EXCLUSIONS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        exclusions.add(line)
    return exclusions


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
        return TIER_WEIGHTS.get(tier, 1.0)
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
        return math.sqrt(max(upvotes, 1))
    if st == "reddit-comment":
        upvotes = source.get("comment_upvotes") or 1
        return math.sqrt(max(upvotes, 1))
    if st == "youtube":
        views = source.get("video_views") or 0
        subs = source.get("channel_subscribers") or 0
        engagement = views + subs / 10
        if engagement <= 0:
            return 1.0
        return math.sqrt(engagement) / YOUTUBE_NORMALIZER
    return 1.0


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
        fm["_path"] = str(path.relative_to(ROOT))
        sources.append(fm)
    return sources


def aggregate(sources):
    movies = defaultdict(
        lambda: {
            "title_counts": defaultdict(int),
            "year_counts": defaultdict(int),
            "score": 0.0,
            "mentions": 0,
            "sources": set(),
        }
    )
    for source in sources:
        for mention in source.get("movies_mentioned") or []:
            nt = mention.get("normalized_title")
            if not nt:
                continue
            movies[nt]["score"] += score_mention(source, mention)
            movies[nt]["mentions"] += 1
            movies[nt]["sources"].add(source["id"])
            if title := mention.get("title"):
                movies[nt]["title_counts"][title] += 1
            if year := mention.get("year"):
                movies[nt]["year_counts"][str(year)] += 1
    return movies


def canonical_title(data, fallback):
    if not data["title_counts"]:
        return fallback
    # most common title wins; break ties on shorter string (cleaner display)
    return max(data["title_counts"].items(), key=lambda kv: (kv[1], -len(kv[0])))[0]


def canonical_year(data):
    if not data["year_counts"]:
        return ""
    # most common year wins; break ties on earliest (original release typically)
    return max(data["year_counts"].items(), key=lambda kv: (kv[1], -int(kv[0])))[0]


def write_csv(ranked, path):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["rank", "normalized_title", "title", "year", "score", "mentions", "num_sources"]
        )
        for i, (nt, data) in enumerate(ranked, 1):
            writer.writerow(
                [
                    i,
                    nt,
                    canonical_title(data, nt),
                    canonical_year(data),
                    f"{data['score']:.3f}",
                    data["mentions"],
                    len(data["sources"]),
                ]
            )


def write_markdown(ranked, path, top_n=100, excluded=None):
    lines = [
        f"# Top {top_n} Dolby Atmos Movies",
        "",
        f"*Auto-generated by [`scoring/score.py`](../scoring/score.py) from {len(ranked)} ranked films across all sources. Do not hand-edit.*",
        "",
        "See [docs/methodology.md](../docs/methodology.md) for how scores are calculated.",
        "",
    ]
    if excluded:
        lines.append(
            f"*{len(excluded)} film(s) captured in sources were excluded from this ranking because they don't have a Dolby Atmos mix. See [`../scoring/excluded.txt`](../scoring/excluded.txt).*"
        )
        lines.append("")
    lines += [
        "| Rank | Film | Year | Score | Mentions | Sources |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for i, (nt, data) in enumerate(ranked[:top_n], 1):
        lines.append(
            f"| {i} | {canonical_title(data, nt)} | {canonical_year(data) or '—'} | "
            f"{data['score']:.2f} | {data['mentions']} | {len(data['sources'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    sources = load_sources()
    movies = aggregate(sources)

    exclusions = load_exclusions()
    excluded_hits = {nt: movies[nt] for nt in exclusions if nt in movies}
    for nt in excluded_hits:
        del movies[nt]

    ranked = sorted(
        movies.items(),
        # primary: score desc; tie-break on mention count desc, then normalized_title asc
        key=lambda kv: (-kv[1]["score"], -kv[1]["mentions"], kv[0]),
    )

    csv_path = OUTPUT_DIR / "ranking.csv"
    md_path = OUTPUT_DIR / "top-100.md"
    write_csv(ranked, csv_path)
    write_markdown(ranked, md_path, top_n=100, excluded=excluded_hits)

    print(f"Scored {len(movies)} distinct films across {len(sources)} sources.")
    if excluded_hits:
        print(f"Excluded {len(excluded_hits)} film(s) (see scoring/excluded.txt):")
        for nt, data in excluded_hits.items():
            print(
                f"  - {canonical_title(data, nt)} "
                f"(would have scored {data['score']:.2f}, {data['mentions']} mentions)"
            )
    print(f"  CSV:      {csv_path.relative_to(ROOT)}")
    print(f"  Top 100:  {md_path.relative_to(ROOT)}")
    print()
    print("Top 25 preview:")
    for i, (nt, data) in enumerate(ranked[:25], 1):
        title = canonical_title(data, nt)
        year = canonical_year(data)
        print(
            f"  {i:>3}. {title} ({year or '—'})  "
            f"score={data['score']:.2f}  mentions={data['mentions']}  sources={len(data['sources'])}"
        )


if __name__ == "__main__":
    main()
