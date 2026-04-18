# Source authority tiers

A living list of every source referenced in this project and the authority tier it's been assigned. Tiers are a manual, defensible judgment — every entry should have a one-line reason, and changes are tracked via git history.

## Tier definitions

| Tier | Meaning | Examples (illustrative, fill in as sources are added) |
|---|---|---|
| `top` | Primary/official references; industry-standard publications with deep AV reviewing history | Dolby's own reference lists, What Hi-Fi reference content |
| `high` | Major tech/entertainment outlets with known editorial standards | IGN, The Verge, Variety, major home-theater magazines |
| `mid` | Established blogs, mid-size outlets, well-known YouTube reviewers with track record | Dedicated AV blogs with multiple years of content |
| `low` | Small personal blogs, SEO-farm listicles, anonymous content | Random "top 10" SEO pages, low-reputation aggregator sites |
| `unknown` | Not yet assessed | Default for any new source until reviewed |

Reddit posts and comments do **not** use this tiering directly — they're weighted by upvotes instead (see [methodology.md](methodology.md)). The tier field in Reddit source files stays `unknown` / is ignored by the algorithm. YouTube videos work the same way, weighted by a combination of channel subscribers and video views.

## Assigned sources

<!--
Format:
### Source name
- **Tier:** high
- **URL / domain:** example.com
- **Reason:** one-line justification
- **First added:** YYYY-MM-DD in source file NNN
-->

### What Hi-Fi?
- **Tier:** top
- **URL / domain:** whathifi.com
- **Reason:** specialist home-cinema and hi-fi publication with decades of editorial reviewing history; AV kit testing is their core beat
- **First added:** 2026-04-18 in source file 001

### TechRadar
- **Tier:** top
- **URL / domain:** techradar.com
- **Reason:** major global tech publication (Future plc) with strong editorial standards and dedicated home-theater coverage
- **First added:** 2026-04-18 in source file 008

### Digital Trends
- **Tier:** top
- **URL / domain:** digitaltrends.com
- **Reason:** major US consumer tech publication with substantial home-theater and AV coverage
- **First added:** 2026-04-18 in source file 012

### Audio Advice
- **Tier:** high
- **URL / domain:** audioadvice.com
- **Reason:** major US AV retailer with long editorial history; strong reputation in the home-theater community. Multiple articles in pool (sources 003, 009) plus YouTube channel (source 017)
- **First added:** 2026-04-18 in source file 003

### Son-Vidéo Blog
- **Tier:** high
- **URL / domain:** blog.son-video.com
- **Reason:** major French AV retailer with detailed technical writeups including per-film sound credits and mix analysis
- **First added:** 2026-04-18 in source file 004

### Stuff
- **Tier:** high
- **URL / domain:** stuff.tv
- **Reason:** established UK consumer tech magazine with editorial standards
- **First added:** 2026-04-18 in source file 005

### hifi.de
- **Tier:** high
- **URL / domain:** hifi.de
- **Reason:** German specialist hi-fi publication with specialist AV focus
- **First added:** 2026-04-18 in source file 006

### Lifewire
- **Tier:** high
- **URL / domain:** lifewire.com
- **Reason:** established Dotdash Meredith tech publication with consumer-tech editorial standards
- **First added:** 2026-04-18 in source file 011

### AV.com
- **Tier:** mid
- **URL / domain:** av.com
- **Reason:** UK AV retailer blog; serviceable but limited editorial track record
- **First added:** 2026-04-18 in source file 002

### Smart Home Sounds
- **Tier:** mid
- **URL / domain:** smart-home-sounds.helpscoutdocs.com
- **Reason:** UK AV retailer blog; generic consensus picks, limited unique editorial value
- **First added:** 2026-04-18 in source file 007

### The Inventory
- **Tier:** mid
- **URL / domain:** theinventory.com
- **Reason:** G/O Media affiliate/shopping blog; decent writing but commerce-driven
- **First added:** 2026-04-18 in source file 015

### Dropsasa
- **Tier:** low
- **URL / domain:** dropsasa.com
- **Reason:** unfamiliar domain; all picks were top-of-pool consensus titles with no unique signal; content-farm characteristics
- **First added:** 2026-04-18 in source file 010

### Polk Audio
- **Tier:** low
- **URL / domain:** polkaudio.com
- **Reason:** speaker manufacturer's own blog; clear commercial interest in promoting Atmos content
- **First added:** 2026-04-18 in source file 013

### Make Life Click
- **Tier:** low
- **URL / domain:** makelifeclick.com
- **Reason:** descriptions read as paraphrases of other AV blogs (notably Son-Vidéo); low-effort content
- **First added:** 2026-04-18 in source file 014

### Sanctuary of Truth
- **Tier:** low
- **URL / domain:** sanctuaryoftruth.com
- **Reason:** AI-generated / SEO-spam content with factual errors (incorrect Atmos launch details, nonsensical phrasing, affiliate spam text)
- **First added:** 2026-04-18 in source file 016
