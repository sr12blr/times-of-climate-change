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

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
STORIES_DIR = BASE_DIR / "stories"
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


def generate(full_rebuild=False):
    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    stories = load_all_stories()
    if not stories:
        print("No stories found.")
        return

    slug_index = build_slug_index(stories)
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # Ensure output directories
    for d in ["story", "today", "archive", "about", "explore", "why", "pass", "static"]:
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
    months = group_by_month(stories)
    template = env.get_template("archive.html")
    html = template.render(
        months=months,
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

    print(f"\nDone. {generated} new story page(s) generated.")
    print(f"Site ready at: {SITE_DIR}/")


if __name__ == "__main__":
    full = "--full" in sys.argv
    if full:
        print("Full rebuild...\n")
    else:
        print("Incremental build...\n")
    generate(full_rebuild=full)
