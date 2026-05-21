---
id: NNN
source_type: youtube
source_name: ""              # the channel name, e.g. "Home Theater Gamer"
source_url: ""               # full YouTube video URL
author: ""                   # host/presenter name, if different from channel name
date_published:              # ISO date YYYY-MM-DD
date_captured:
title: ""                    # video title
authority_tier: unknown      # YouTube videos typically weighted by engagement; tier usually unused
is_ranked_list: false        # true if the video's scene list is explicitly numbered
list_length:                 # integer — total scenes covered in the video

# YouTube-specific fields
channel_subscribers:         # integer at time of capture
video_views:                 # integer at time of capture
video_likes:                 # integer, if visible (YouTube sometimes hides)

scenes_mentioned:
  - movie_title: ""
    movie_year:
    normalized_title: ""
    scene_name: ""
    normalized_scene_id: ""  # "{normalized_title}--{kebab-case-scene-name}"
    timestamp:               # "HH:MM:SS" or "HH:MM:SS-HH:MM:SS"; null if not given
    rank:
    description: ""
---
