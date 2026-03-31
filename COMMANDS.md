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
