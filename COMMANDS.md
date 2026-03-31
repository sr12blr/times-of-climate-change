# Useful Commands for Times of Climate Change

## Regenerate Sitemap
After publishing new stories, run this to update the sitemap for Google indexing:

```bash
python3 /Users/sailee/climate-v2/generate_sitemap.py
```

Then commit and push to GitHub:
```bash
cd /Users/sailee/climate-v2
git add docs/sitemap.xml
git commit -m "Update sitemap.xml"
git push
```

## Build/Generate Site
Full rebuild of the static site:
```bash
python3 /Users/sailee/climate-v2/generate_site.py --full
```

Incremental build (faster):
```bash
python3 /Users/sailee/climate-v2/generate_site.py
```

## Preview Site Locally
Start the preview server (configured in `.claude/launch.json` as "climate-v2"):
```bash
python3 -m http.server 8081 -d /Users/sailee/climate-v2/docs
```

Then open: http://localhost:8081

## Generate WhatsApp Cover
Generate a WhatsApp channel cover image (1080x1080) for stories:

```bash
# Latest story
python3 /Users/sailee/climate-v2/generate_wa_cover.py

# Specific story by date
python3 /Users/sailee/climate-v2/generate_wa_cover.py 2026-03-27

# Generate and open in browser
python3 /Users/sailee/climate-v2/generate_wa_cover.py --open
```

Output: `wa_cover.html` (screenshot at 1080x1080 for best results)
