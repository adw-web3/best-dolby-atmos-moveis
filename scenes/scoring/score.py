"""Aggregate scene mentions across all sources and produce the ranked Top 100 scenes.

Algorithm (v1) — see docs/methodology.md for the full rationale.

    per-mention score = tier x rank x engagement
    raw_score         = sum of per-mention scores for a scene
    final_score       = raw_score x breadth_multiplier

Tier (articles only):   top=3.0  high=2.0  mid=1.0  low=0.25  unknown=0.25
                        Reddit / YouTube are never tier-weighted (tier = 1.0).
Rank (ranked lists):    1 + ((list_length - rank + 1) / list_length) x 0.5
Engagement
  - articles:           1.0  (weighted by tier instead)
  - Reddit:             1 + ln(upvotes) / REDDIT_K
  - YouTube:            1 + ln(max(views + subs/10, YT_BASE) / YT_BASE) / YT_K
Breadth:                1 + BREADTH_B x ln(num_sources)

`num_sources` is the count of distinct source files (Reddit threads + articles +
videos) that mention the scene, so a scene corroborated across many independent
threads outranks one a single popular comment happens to list.

Scenes whose film has no Dolby Atmos home mix are dropped from the ranking by
joining each scene's `normalized_title` against the shared movie-side exclusion
list (../../scoring/excluded.txt).
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent              # scenes/
SOURCES_DIR = ROOT / "sources"
OUTPUT_DIR = ROOT / "output"
EXCLUSIONS_FILE = ROOT.parent / "scoring" / "excluded.txt"  # shared movie-side list
TV_SHOWS_FILE = Path(__file__).resolve().parent / "tv-shows.txt"      # films-only: drop TV
TIMESTAMPS_FILE = Path(__file__).resolve().parent / "timestamps.csv"  # researched overrides
DESCRIPTIONS_FILE = Path(__file__).resolve().parent / "descriptions.csv"  # cleaned copy
SCENE_NAMES_FILE = Path(__file__).resolve().parent / "scene-names.csv"    # cleaned names

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


def load_timestamp_overrides() -> dict:
    """Researched timestamps for scenes that no captured source dated.

    Captured sources only ever supply a timestamp if the source itself stated
    one. timestamps.csv carries figures explicitly stated elsewhere (chapter
    databases, scene guides) — each row cites where. An override takes
    precedence over any source-derived timestamp for that scene.
    """
    overrides = {}
    if TIMESTAMPS_FILE.exists():
        with TIMESTAMPS_FILE.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sid = (row.get("normalized_scene_id") or "").strip()
                ts = (row.get("timestamp") or "").strip()
                if sid and ts:
                    overrides[sid] = ts
    return overrides


def load_description_overrides() -> dict:
    """Editor-cleaned scene descriptions for the published output.

    A scene's description otherwise comes verbatim from the longest captured
    source mention. descriptions.csv supplies copy-edited versions (source
    attribution removed, em dashes cleared) for the published-facing CSVs,
    without altering what the captured sources actually wrote.
    """
    overrides = {}
    if DESCRIPTIONS_FILE.exists():
        with DESCRIPTIONS_FILE.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sid = (row.get("normalized_scene_id") or "").strip()
                desc = (row.get("description") or "").strip()
                if sid and desc:
                    overrides[sid] = desc
    return overrides


def load_scene_name_overrides() -> dict:
    """Editor-cleaned scene names for the published output.

    A scene's name otherwise comes from its most common source label.
    scene-names.csv supplies copy-edited versions (capture artifacts like
    "(Ch 6)" / "(Rears)" / "(Tokyo?)" removed) without altering the sources.
    """
    overrides = {}
    if SCENE_NAMES_FILE.exists():
        with SCENE_NAMES_FILE.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sid = (row.get("normalized_scene_id") or "").strip()
                name = (row.get("scene_name") or "").strip()
                if sid and name:
                    overrides[sid] = name
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
        fm["_key"] = str(path.relative_to(SOURCES_DIR))  # stable, unique per file
        sources.append(fm)
    return sources


def aggregate(sources):
    scenes = defaultdict(
        lambda: {
            "name_counts": defaultdict(int),
            "movie_counts": defaultdict(int),
            "year_counts": defaultdict(int),
            "title_counts": defaultdict(int),       # normalized_title (exclusion join)
            "timestamp_counts": defaultdict(int),
            "descriptions": [],
            "raw": 0.0,
            "mentions": 0,
            "sources": set(),
        }
    )
    for source in sources:
        for mention in source.get("scenes_mentioned") or []:
            sid = mention.get("normalized_scene_id")
            if not sid:
                continue
            data = scenes[sid]
            data["raw"] += score_mention(source, mention)
            data["mentions"] += 1
            data["sources"].add(source["_key"])
            if name := mention.get("scene_name"):
                data["name_counts"][name] += 1
            if movie := mention.get("movie_title"):
                data["movie_counts"][movie] += 1
            if year := mention.get("movie_year"):
                data["year_counts"][str(year)] += 1
            if nt := mention.get("normalized_title"):
                data["title_counts"][nt] += 1
            if ts := mention.get("timestamp"):
                data["timestamp_counts"][str(ts)] += 1
            if desc := mention.get("description"):
                data["descriptions"].append(desc.strip())
    for data in scenes.values():
        data["score"] = data["raw"] * (1.0 + BREADTH_B * math.log(len(data["sources"])))
    return scenes


def _most_common(counts, fallback="", tie_key=lambda kv: -len(kv[0])):
    """Most frequent key; ties broken by tie_key (default: shorter string)."""
    if not counts:
        return fallback
    return max(counts.items(), key=lambda kv: (kv[1], tie_key(kv)))[0]


def canonical_name(data, fallback):
    # most frequent scene_name wins; ties broken toward a moderate-length name
    # (~24 chars) so the label avoids both terse ("Intro") and over-verbose
    # ("Flight attack — bomb deployment (chapter 13)") extremes.
    return _most_common(data["name_counts"], fallback, tie_key=lambda kv: -abs(len(kv[0]) - 24))


def canonical_movie(data, fallback=""):
    return _most_common(data["movie_counts"], fallback)


def canonical_year(data):
    # most common year wins; ties broken on earliest
    return _most_common(data["year_counts"], "", tie_key=lambda kv: -int(kv[0]))


def canonical_title(data, fallback):
    return _most_common(data["title_counts"], fallback)


def canonical_timestamp(data):
    # most common timestamp; for a range ("HH:MM:SS-HH:MM:SS") keep only the start
    ts = _most_common(data["timestamp_counts"], "")
    return ts.split("-")[0] if ts else ""


def canonical_description(data):
    # the longest description across the scene's mentions — usually the most
    # informative; sources write one-liners so length is a fair proxy.
    return max(data["descriptions"], key=len) if data["descriptions"] else ""


def write_csv(ranked, path, overrides, names, descriptions, limit=None):
    rows = ranked[:limit] if limit else ranked
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "rank",
                "movie_title",
                "movie_year",
                "normalized_title",
                "scene_name",
                "normalized_scene_id",
                "timestamp",
                "score",
                "mentions",
                "num_sources",
                "description",
            ]
        )
        for i, (sid, data) in enumerate(rows, 1):
            writer.writerow(
                [
                    i,
                    canonical_movie(data),
                    canonical_year(data),
                    canonical_title(data, sid.split("--")[0]),
                    names.get(sid) or canonical_name(data, sid),
                    sid,
                    overrides.get(sid) or canonical_timestamp(data),
                    f"{data['score']:.3f}",
                    data["mentions"],
                    len(data["sources"]),
                    descriptions.get(sid) or canonical_description(data),
                ]
            )


def write_markdown(ranked, path, overrides, names, top_n=100, excluded=None):
    lines = [
        f"# Top {top_n} Dolby Atmos Demo Scenes",
        "",
        f"*Auto-generated by [`scoring/score.py`](../scoring/score.py) from "
        f"{len(ranked)} ranked scenes across all sources. Do not hand-edit.*",
        "",
        "See [docs/methodology.md](../docs/methodology.md) for how scores are calculated.",
        "",
        "*Feature films only — scenes from TV shows are not ranked.*",
        "",
    ]
    if excluded:
        lines.append(
            f"*{len(excluded)} scene(s) captured in sources were excluded from this "
            f"ranking because their film has no Dolby Atmos home mix. "
            f"See [`../../scoring/excluded.txt`](../../scoring/excluded.txt).*"
        )
        lines.append("")
    lines += [
        "| Rank | Film | Scene | Year | Timestamp | Score | Mentions | Sources |",
        "|---:|---|---|---:|---|---:|---:|---:|",
    ]
    for i, (sid, data) in enumerate(ranked[:top_n], 1):
        lines.append(
            f"| {i} | {canonical_movie(data, '—')} | {names.get(sid) or canonical_name(data, sid)} | "
            f"{canonical_year(data) or '—'} | {overrides.get(sid) or canonical_timestamp(data) or ''} | "
            f"{data['score']:.2f} | {data['mentions']} | {len(data['sources'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    sources = load_sources()
    scenes = aggregate(sources)

    # Drop scenes from TV shows — the ranking covers feature films only.
    tv_shows = load_title_list(TV_SHOWS_FILE)
    tv_hits = {
        sid: data
        for sid, data in scenes.items()
        if canonical_title(data, sid.split("--")[0]) in tv_shows
    }
    for sid in tv_hits:
        del scenes[sid]

    # Drop scenes whose film has no Atmos home mix (join on normalized_title).
    exclusions = load_title_list(EXCLUSIONS_FILE)
    excluded_hits = {
        sid: data
        for sid, data in scenes.items()
        if canonical_title(data, sid.split("--")[0]) in exclusions
    }
    for sid in excluded_hits:
        del scenes[sid]

    ranked = sorted(
        scenes.items(),
        # primary: score desc; tie-break on mention count desc, then scene id asc
        key=lambda kv: (-kv[1]["score"], -kv[1]["mentions"], kv[0]),
    )

    overrides = load_timestamp_overrides()
    descriptions = load_description_overrides()
    names = load_scene_name_overrides()
    csv_path = OUTPUT_DIR / "ranking.csv"
    top_csv_path = OUTPUT_DIR / "top-100.csv"
    md_path = OUTPUT_DIR / "top-100.md"
    write_csv(ranked, csv_path, overrides, names, descriptions)
    write_csv(ranked, top_csv_path, overrides, names, descriptions, limit=100)
    write_markdown(ranked, md_path, overrides, names, top_n=100, excluded=excluded_hits)

    print(f"Scored {len(scenes)} distinct scenes across {len(sources)} sources.")
    if tv_hits:
        print(f"Dropped {len(tv_hits)} TV-show scene(s) (films-only ranking, see scoring/tv-shows.txt).")
    if excluded_hits:
        print(f"Excluded {len(excluded_hits)} scene(s) (non-Atmos film, see scoring/excluded.txt).")
    print(f"  Full CSV:  {csv_path.relative_to(ROOT)}")
    print(f"  Top 100:   {top_csv_path.relative_to(ROOT)} / {md_path.relative_to(ROOT)}")
    print()
    print("Top 25 preview:")
    for i, (sid, data) in enumerate(ranked[:25], 1):
        print(
            f"  {i:>3}. {canonical_name(data, sid)} — {canonical_movie(data, '?')}  "
            f"score={data['score']:.2f}  mentions={data['mentions']}  "
            f"sources={len(data['sources'])}"
        )


if __name__ == "__main__":
    main()
