# The Times of Climate Change — Project Context

## What This Is
A daily climate news website for India called **"The Times of Climate Change"**. One story per day that connects climate/environment to daily life in India — food prices, commute, water, health.

## Architecture

### News Collection Pipeline
```
Cron (daily 6 AM) → collect.py → [RSS / HTML scraper] → Filter → Deduplicate → data/YYYY-MM-DD.json
```
- **7 sources**: Mongabay India, Down to Earth, The Hindu, Indian Express, The Guardian, Scroll.in, Google News
- Cross-day deduplication (7-day lookback) to avoid repeats
- Crontab: `0 6 * * * cd /Users/sailee/climate-news-collector && /usr/bin/python3 collect.py >> /Users/sailee/climate-news-collector/logs/cron.log 2>&1`

### Story Publishing
- Stories are JSON files in `stories/YYYY-MM-DD.json`
- `shortlist.py` scores collected articles to help pick the daily story
- `generate_site.py` builds static HTML from Jinja2 templates into `site/`
- `generate_site.py --full` for full rebuild, default is incremental
- Preview server: `python3 -m http.server 8080` from `site/` dir (configured in `.claude/launch.json` as "climate-site")

### File Structure
```
climate-news-collector/
    collect.py           # Main collection entry point (cron target)
    config.py            # Sources, keywords, paths
    sources.py           # RSS fetching + Scroll.in scraper + Google News
    filters.py           # Keyword filtering + dedup
    shortlist.py         # Score and rank articles for story selection
    publish.py           # Story creation helper
    generate_site.py     # Static site generator (Jinja2 → HTML)
    requirements.txt     # feedparser, requests, beautifulsoup4, jinja2
    data/                # Daily JSON collection files (YYYY-MM-DD.json)
    stories/             # Published story JSON files
    templates/           # Jinja2 templates (base.html, index.html, story.html, story_content.html, archive.html, about.html)
    site/                # Generated static site output
    site/static/style.css
    logs/                # Log files
```

## Story JSON Format
```json
{
  "date": "YYYY-MM-DD",
  "slug": "url-friendly-slug",
  "title": "Story Title",
  "what_talking_about": ["bullet 1", "bullet 2"],
  "why_care": ["bullet 1", "bullet 2"],
  "why_now": ["optional section - bullet 1"],
  "what_can_we_do": ["optional section - bullet 1"],
  "tags": ["Tag1", "Tag2"],
  "sources": [{"title": "Source Name: Article Title", "url": "https://..."}],
  "related_stories": ["slug-of-related-story"]
}
```

## Editorial Style
- Simple, conversational, relatable for common people
- Lead with impact on daily life (food prices, water, health, commute)
- No jargon, no long reports
- Always verify source attribution
- Sections: "What are we talking about?" → "Why should you care?" → optional "Why now?" → optional "What can we do about it?"

## Website Design
- **Font**: Lato (Google Fonts) for body and story titles, Georgia/serif for site title and footer
- **Colors**: White background (#ffffff), dark maroon site title (#6b1c2a), forest green story titles (#2c5f4a)
- **Layout**: Max 1000px width, two-column grid with sidebar for related stories ("More Threads to Tug On")
- **Nav**: Today | Archive | About
- **Footer**: Serif, maroon, centered
- **Responsive**: Single column on mobile (<600px)
- CSS cache-busting via file modification timestamp (`?v=timestamp`)

## Current Stories (as of March 23, 2026)
1. **Nov 12, 2025**: 'I just want to breathe': Rare protests over air pollution in New Delhi
2. **Jan 15, 2026**: Devastating fire in the Valley of flowers, triggered by an unusually dry winter
3. **Mar 17, 2026**: A village in Maharashtra is sitting on biodiversity gold (Down To Earth)
4. **Mar 18, 2026**: Too Hot to Move — Lancet heat study
5. **Mar 19, 2026**: Local solution to the LPG crisis
6. **Mar 20, 2026**: The Dark Side of Solar: Why Rajasthan's Villagers are fighting to Stop a Solar Project
7. **Mar 21, 2026**: The end of Spring: India Jumps Straight from Winter to Summer
8. **Mar 22, 2026**: The World Is Water-Bankrupt. India Is One of the Worst Hit. (World Water Day)

## Pending Tasks
- **Publish to GitHub Pages** — user wants to share the site for feedback. Need to install `gh` CLI (no Homebrew on this machine), initialize git repo, push to GitHub, enable Pages
- **Pick story for March 23** — news collection cron should have run at 6 AM
- Story shortlist scoring tweaks (human interest bonus, surprising connection bonus) from earlier sessions
- Clean up unused `.site-title-prefix` CSS (leftover from old italic attempt)
