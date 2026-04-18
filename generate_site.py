#!/usr/bin/env python3
"""
Static site generator for The Times of Climate Change — v2.

Usage:
    python3 generate_site.py              # Incremental build
    python3 generate_site.py --full       # Full rebuild
"""

import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, pass_context

BASE_DIR = Path(__file__).parent
STORIES_DIR = BASE_DIR / "stories"
PUZZLES_DIR = BASE_DIR / "puzzles"
SITE_DIR = BASE_DIR / "docs"
TEMPLATES_DIR = BASE_DIR / "templates"

IMPACT_CATEGORIES = [
    {"name": "Food", "label": "The food on your plate", "slug": "food", "icon": "🍽️"},
    {"name": "Water", "label": "The water that sustains you", "slug": "water", "icon": "🚰"},
    {"name": "Air quality", "label": "The air you breathe", "slug": "air-quality", "icon": "😷"},
    {"name": "Health", "label": "Your health and fitness", "slug": "health", "icon": "👨‍⚕️"},
    {"name": "Heat", "label": "How hot your days get", "slug": "heat", "icon": "🥵"},
    {"name": "Inflation", "label": "What things cost you", "slug": "inflation", "icon": "🛒"},
    {"name": "Mobility", "label": "How you get around", "slug": "mobility", "icon": "🛺"},
    {"name": "Biodiversity", "label": "The birds, bees and trees", "slug": "biodiversity", "icon": "🦚"},
]


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].rstrip("-")


def load_all_stories():
    stories = []
    for f in sorted(STORIES_DIR.glob("*.json"), reverse=True):
        try:
            with open(f, "r") as fh:
                story = json.load(fh)
            if not story.get("title"):
                continue
            if not story.get("slug"):
                story["slug"] = slugify(story["title"])
            try:
                dt = datetime.strptime(story["date"], "%Y-%m-%d")
                story["date_display"] = dt.strftime("%B %d, %Y")
                story["date_short"] = dt.strftime("%b %d")
                story["date_month"] = dt.strftime("%B %Y")
            except ValueError:
                story["date_display"] = story["date"]
                story["date_short"] = story["date"]
                story["date_month"] = "Unknown"
            stories.append(story)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: skipping {f.name} ({e})")
    return stories


def build_slug_index(stories):
    return {s["slug"]: s for s in stories}


def get_related(story, slug_index):
    related = []
    for slug in story.get("related_stories", []):
        if slug in slug_index:
            related.append(slug_index[slug])
    return related


def group_by_month(stories):
    months = defaultdict(list)
    for s in stories:
        months[s["date_month"]].append(s)
    seen = []
    result = []
    for s in stories:
        if s["date_month"] not in seen:
            seen.append(s["date_month"])
            result.append((s["date_month"], months[s["date_month"]]))
    return result


def group_by_year(stories):
    """Group stories by year for archive display"""
    from collections import OrderedDict
    grouped = OrderedDict()
    for story in stories:
        year = story["date"][:4]
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(story)
    return list(grouped.items())


def group_by_impact(stories):
    impact_map = {}
    for cat in IMPACT_CATEGORIES:
        matching = [s for s in stories if cat["name"] in s.get("tag_impact", [])]
        impact_map[cat["slug"]] = {
            "name": cat["name"],
            "label": cat["label"],
            "slug": cat["slug"],
            "icon": cat["icon"],
            "count": len(matching),
            "stories": matching,
        }
    return impact_map


def load_all_puzzles():
    """Load all puzzle JSON files from puzzles/ directory"""
    puzzles = []
    PUZZLES_DIR.mkdir(parents=True, exist_ok=True)

    for f in sorted(PUZZLES_DIR.glob("*.json"), reverse=True):
        try:
            with open(f, "r") as fh:
                puzzle = json.load(fh)

            # Parse date and create archive title
            try:
                dt = datetime.strptime(puzzle["date"], "%Y-%m-%d")
                puzzle["date_display"] = dt.strftime("%B %d, %Y")
                # Create archive number from date (YYMMDD)
                puzzle["archive_number"] = dt.strftime("%y%m%d")
                puzzle["archive_title"] = f"Torchlight - {puzzle['archive_number']}"
                puzzle["slug"] = puzzle["archive_number"]
            except ValueError:
                puzzle["date_display"] = puzzle.get("date", "Unknown")
                puzzle["archive_title"] = "Unknown"
                puzzle["slug"] = "unknown"

            puzzles.append(puzzle)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: skipping puzzle {f.name} ({e})")

    return puzzles


def generate(full_rebuild=False):
    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    stories = load_all_stories()
    if not stories:
        print("No stories found.")
        return

    slug_index = build_slug_index(stories)
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # Ensure output directories
    for d in ["story", "today", "archive", "about", "explore", "why", "pass", "static", "torchlight"]:
        (SITE_DIR / d).mkdir(parents=True, exist_ok=True)

    # CSS cache-busting
    css_file = SITE_DIR / "static" / "style.css"
    css_version = int(css_file.stat().st_mtime) if css_file.exists() else 0

    impact_map = group_by_impact(stories)
    categories = [impact_map[cat["slug"]] for cat in IMPACT_CATEGORIES]

    latest = stories[0]
    generated = 0

    # 1. Landing page (/)
    template = env.get_template("index.html")
    html = template.render(
        is_landing=True,
        root_path="",
        css_path=f"static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "index.html", "w") as f:
        f.write(html)
    print("  Generated: index.html (landing)")

    # 2. Why page (/why/)
    template = env.get_template("why.html")
    html = template.render(
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "why" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: why/")

    # 3. Pass page (/pass/)
    template = env.get_template("pass.html")
    html = template.render(
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "pass" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: pass/")

    # 4. Today page (/today/) — latest story
    related = get_related(latest, slug_index)
    template = env.get_template("today.html")
    html = template.render(
        story=latest,
        related=related,
        active_nav="today",
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "today" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: today/")

    # 5. Individual story pages
    for i, story in enumerate(stories):
        story_dir = SITE_DIR / "story" / story["slug"]
        story_file = story_dir / "index.html"

        if not full_rebuild and story_file.exists():
            continue

        story_dir.mkdir(parents=True, exist_ok=True)
        related = get_related(story, slug_index)

        template = env.get_template("story.html")
        html = template.render(
            story=story,
            related=related,
            active_nav="",
            root_path="../../",
            css_path=f"../../static/style.css?v={css_version}",
        )
        with open(story_file, "w") as f:
            f.write(html)
        generated += 1
        print(f"  Generated: story/{story['slug']}/")

    # 6. Archive
    stories_by_year = group_by_year(stories)
    template = env.get_template("archive.html")
    html = template.render(
        stories_by_year=stories_by_year,
        active_nav="archive",
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "archive" / "index.html", "w") as f:
        f.write(html)
    print(f"  Generated: archive/ ({len(stories)} stories)")

    # 7. Explore / Getting Real — category cards
    template = env.get_template("explore.html")
    html = template.render(
        categories=categories,
        active_nav="explore",
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "explore" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: explore/")

    # Individual category pages
    template = env.get_template("explore_category.html")
    for cat_slug, cat_data in impact_map.items():
        cat_dir = SITE_DIR / "explore" / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)
        html = template.render(
            category=cat_data,
            stories=cat_data["stories"],
            active_nav="explore",
            root_path="../../",
            css_path=f"../../static/style.css?v={css_version}",
        )
        with open(cat_dir / "index.html", "w") as f:
            f.write(html)
        print(f"  Generated: explore/{cat_slug}/ ({cat_data['count']} stories)")

    # 8. About
    template = env.get_template("about.html")
    html = template.render(
        active_nav="about",
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(SITE_DIR / "about" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: about/")

    # 9. April Fools quiz page
    april_fools_dir = SITE_DIR / "april-fools"
    april_fools_dir.mkdir(parents=True, exist_ok=True)
    template = env.get_template("april-fools.html")
    html = template.render(
        active_nav="",
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )
    with open(april_fools_dir / "index.html", "w") as f:
        f.write(html)
    print("  Generated: april-fools/")

    # 10. Torchlight - today's puzzle
    puzzles = load_all_puzzles()
    if puzzles:
        from zoneinfo import ZoneInfo
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        today_puzzle = next(
            (p for p in puzzles if datetime.strptime(p["date"], "%Y-%m-%d").date() <= today),
            puzzles[0]
        )
        puzzle_json = {
            "date": today_puzzle["date"],
            "categories": today_puzzle["categories"],
            "fun_fact": today_puzzle.get("fun_fact", ""),
            "author": today_puzzle.get("author", "")
        }
        template = env.get_template("torchlight.html")
        html = template.render(
            puzzle=today_puzzle,
            puzzle_json=puzzle_json,
            active_nav="",
            root_path="../",
            css_path=f"../static/style.css?v={css_version}",
        )
        with open(SITE_DIR / "torchlight" / "index.html", "w") as f:
            f.write(html)
        print("  Generated: torchlight/")

        # Torchlight archive page
        past_puzzles = [p for p in puzzles if datetime.strptime(p["date"], "%Y-%m-%d").date() <= today]
        (SITE_DIR / "torchlight" / "archive").mkdir(parents=True, exist_ok=True)
        template = env.get_template("torchlight_archive.html")
        html = template.render(
            puzzles=past_puzzles,
            active_nav="",
            root_path="../",
            css_path=f"../static/style.css?v={css_version}",
        )
        with open(SITE_DIR / "torchlight" / "archive" / "index.html", "w") as f:
            f.write(html)
        print("  Generated: torchlight/archive/")

        # Individual archive puzzle pages
        for puzzle in past_puzzles[1:]:  # Skip today's puzzle, it's already generated
            puzzle_dir = SITE_DIR / "torchlight" / "archive" / puzzle["slug"]
            puzzle_dir.mkdir(parents=True, exist_ok=True)
            puzzle_json = {
                "date": puzzle["date"],
                "categories": puzzle["categories"],
                "fun_fact": puzzle.get("fun_fact", ""),
                "author": puzzle.get("author", "")
            }
            template = env.get_template("torchlight.html")
            html = template.render(
                puzzle=puzzle,
                puzzle_json=puzzle_json,
                active_nav="",
                root_path="../../../",
                css_path=f"../../../static/style.css?v={css_version}",
            )
            with open(puzzle_dir / "index.html", "w") as f:
                f.write(html)
        print(f"  Generated: torchlight/archive/ ({len(puzzles)-1} archive puzzles)")

    # 11. Sitemap
    BASE_URL = "https://timesofclimatechange.com"
    today = date.today().isoformat()
    static_pages = [
        ("", "daily", "1.0"),
        ("today/", "daily", "1.0"),
        ("archive/", "daily", "0.9"),
        ("torchlight/", "daily", "0.9"),
        ("torchlight/archive/", "weekly", "0.8"),
        ("explore/", "weekly", "0.8"),
        ("explore/food/", "weekly", "0.7"),
        ("explore/water/", "weekly", "0.7"),
        ("explore/air-quality/", "weekly", "0.7"),
        ("explore/health/", "weekly", "0.7"),
        ("explore/heat/", "weekly", "0.7"),
        ("explore/inflation/", "weekly", "0.7"),
        ("explore/mobility/", "weekly", "0.7"),
        ("explore/biodiversity/", "weekly", "0.7"),
        ("about/", "monthly", "0.6"),
        ("why/", "monthly", "0.6"),
    ]
    urls = []
    for path, freq, pri in static_pages:
        urls.append(f"""  <url>
    <loc>{BASE_URL}/{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""")
    for s in sorted(stories, key=lambda x: x["date"], reverse=True):
        urls.append(f"""  <url>
    <loc>{BASE_URL}/story/{s['slug']}/</loc>
    <lastmod>{s['date']}</lastmod>
    <changefreq>never</changefreq>
    <priority>0.8</priority>
  </url>""")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls) + "\n"
    sitemap += "</urlset>\n"
    with open(SITE_DIR / "sitemap.xml", "w") as f:
        f.write(sitemap)
    print("  Generated: sitemap.xml")

    print(f"\nDone. {generated} new story page(s) generated.")
    print(f"Site ready at: {SITE_DIR}/")


if __name__ == "__main__":
    full = "--full" in sys.argv
    if full:
        print("Full rebuild...\n")
    else:
        print("Incremental build...\n")
    generate(full_rebuild=full)
