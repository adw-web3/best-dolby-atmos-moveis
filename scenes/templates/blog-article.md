---
id: NNN
source_type: blog
source_name: ""              # e.g. "AVForums", "The Master Switch"
source_url: ""
author: ""
date_published:              # ISO date YYYY-MM-DD, or null if unknown
date_captured:               # ISO date the entry was added to this repo
title: ""
authority_tier: unknown      # top | high | mid | low | unknown — see ../../docs/source-authority-tiers.md (shared with movies)
is_ranked_list: false        # true if the article presents scenes in a numbered ranking
list_length:                 # integer — total scenes covered by the source; null if just passing mentions
scenes_mentioned:
  - movie_title: ""
    movie_year:              # integer; null if unknown
    normalized_title: ""     # lowercase, hyphenated, no punctuation — joins with the movie ranking
    scene_name: ""           # human-readable, taken from the source
    normalized_scene_id: ""  # "{normalized_title}--{kebab-case-scene-name}"
    timestamp:               # "HH:MM:SS" or "HH:MM:SS-HH:MM:SS"; null if not given
    rank:                    # integer if part of a ranked scene list; null otherwise
    description: ""          # one-line paraphrase of why the source picks this scene
---
