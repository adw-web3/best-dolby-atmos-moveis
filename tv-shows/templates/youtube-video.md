---
id: NNN
source_type: youtube
source_name: ""              # the channel name, e.g. "Theater At Home"
source_url: ""               # full YouTube video URL
author: ""                   # host/presenter name, if different from channel name
date_published:              # ISO date YYYY-MM-DD
date_captured:
title: ""                    # video title
authority_tier: unknown      # YouTube videos typically weighted by engagement; tier usually unused
is_ranked_list: false        # true if the video's show list is explicitly numbered
list_length:                 # integer — total shows covered in the video

# YouTube-specific fields
channel_subscribers:         # integer at time of capture
video_views:                 # integer at time of capture
video_likes:                 # integer, if visible (YouTube sometimes hides)

shows_mentioned:
  - show_title: ""
    first_air_year:          # integer; null if unknown
    normalized_title: ""     # lowercase, hyphenated series slug — the aggregation key
    platform:                # streaming platform / network if the video states it; null otherwise
    episode_ref:             # episode(s)/season(s) cited, e.g. "S4E6" or "S1; S4E6"; null if series-wide
    rank:                    # integer if part of a ranked list; null otherwise
    description: ""          # one-line paraphrase of why the video picks this show
---
