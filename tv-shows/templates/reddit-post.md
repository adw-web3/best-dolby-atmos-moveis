---
id: NNN
source_type: reddit-post
source_name: ""              # subreddit display form, e.g. "r/hometheater"
source_url: ""               # full permalink to the post
author: ""                   # OP's username (without u/)
date_published:              # ISO date YYYY-MM-DD
date_captured:
title: ""                    # the post title
authority_tier: unknown      # Reddit posts typically unused; scoring leans on upvotes instead
is_ranked_list: false        # rarely true, but possible (e.g. OP lists their top 10 Atmos shows)
list_length:

# Reddit-specific fields
subreddit: ""                # e.g. "r/hometheater", "r/DolbyAtmosContent"
post_upvotes:                # integer
post_num_comments:           # integer
post_flair: ""               # if any

shows_mentioned:
  - show_title: ""
    first_air_year:          # integer; null if unknown
    normalized_title: ""     # lowercase, hyphenated series slug — the aggregation key
    platform:                # streaming platform / network if the voice states it; null otherwise
    episode_ref:             # episode(s)/season(s) cited, e.g. "S4E6" or "S1; S4E6"; null if series-wide
    rank:                    # integer if part of a ranked list; null otherwise
    description: ""          # one-line paraphrase of why this voice picks the show
    mentioned_by: "OP"       # "OP" or a commenter's username — lets us weight OP body vs comments
    comment_upvotes:         # if the mention came from a specific comment in the thread
---
