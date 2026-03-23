#!/usr/bin/env python3
"""
Static site generator for Climate Daily India.

Usage:
    python3 generate_site.py              # Incremental: generate new/updated pages
    python3 generate_site.py --full       # Full rebuild of all pages

Reads stories from stories/*.json, generates HTML into site/.
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


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].rstrip("-")


def load_all_stories():
    """Load all story JSON files, sorted newest first."""
    stories = []
    for f in sorted(STORIES_DIR.glob("*.json"), reverse=True):
        try:
            with open(f, "r") as fh:
                story = json.load(fh)

            # Skip empty templates
            if not story.get("title"):
                continue

            # Auto-generate slug if missing
            if not story.get("slug"):
                story["slug"] = slugify(story["title"])

            # Add display-friendly date
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
    """Build a lookup from slug to story."""
    return {s["slug"]: s for s in stories}


def get_related(story, slug_index):
    """Resolve related_stories slugs to actual story objects."""
    related = []
    for slug in story.get("related_stories", []):
        if slug in slug_index:
            related.append(slug_index[slug])
    return related


def group_by_month(stories):
    """Group stories by month for the archive page."""
    months = defaultdict(list)
    for s in stories:
        months[s["date_month"]].append(s)

    # Return as ordered list of (month_label, stories)
    seen = []
    result = []
    for s in stories:
        if s["date_month"] not in seen:
            seen.append(s["date_month"])
            result.append((s["date_month"], months[s["date_month"]]))
    return result


# Impact categories: name, slug, icon
IMPACT_CATEGORIES = [
    {"name": "Food", "slug": "food", "icon": "\U0001F33E"},
    {"name": "Water", "slug": "water", "icon": "\U0001F4A7"},
    {"name": "Air quality", "slug": "air-quality", "icon": "\U0001F32C\uFE0F"},
    {"name": "Health", "slug": "health", "icon": "\U0001FA7A"},
    {"name": "Heat", "slug": "heat", "icon": "\U0001F321\uFE0F"},
    {"name": "Inflation", "slug": "inflation", "icon": "\U0001F4B8"},
    {"name": "Mobility", "slug": "mobility", "icon": "\U0001F6A6"},
    {"name": "Biodiversity", "slug": "biodiversity", "icon": "\U0001F33F"},
]


def group_by_impact(stories):
    """Group stories by impact tag categories."""
    impact_map = {}
    for cat in IMPACT_CATEGORIES:
        matching = [s for s in stories if cat["name"] in s.get("tag_impact", [])]
        impact_map[cat["slug"]] = {
            "name": cat["name"],
            "slug": cat["slug"],
            "icon": cat["icon"],
            "count": len(matching),
            "stories": matching,
        }
    return impact_map


def generate(full_rebuild=False):
    """Generate the static site."""
    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    stories = load_all_stories()
    if not stories:
        print("No stories found in stories/. Create one with: python3 publish.py create")
        return

    slug_index = build_slug_index(stories)
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # Ensure output directories exist
    (SITE_DIR / "story").mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "archive").mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "about").mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "explore").mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "static").mkdir(parents=True, exist_ok=True)

    # Cache-busting: use CSS file modification time
    css_file = SITE_DIR / "static" / "style.css"
    css_version = int(css_file.stat().st_mtime) if css_file.exists() else 0

    # Build date for top bar
    top_bar_date = date.today().strftime("%A, %B %d, %Y")

    # Impact categories for the "What's at Stake" grid
    impact_map = group_by_impact(stories)
    categories = [impact_map[cat["slug"]] for cat in IMPACT_CATEGORIES]

    generated = 0

    # 1. Generate individual story pages
    for story in stories:
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
            categories=categories,
            link_title=False,
            active_nav="today",
            top_bar_date=top_bar_date,
            root_path="../../",
            css_path=f"../../static/style.css?v={css_version}",
        )

        with open(story_file, "w") as f:
            f.write(html)
        generated += 1
        print(f"  Generated: story/{story['slug']}/")

    # 2. Generate index.html (always — shows latest story)
    latest = stories[0]
    related = get_related(latest, slug_index)

    template = env.get_template("index.html")
    html = template.render(
        story=latest,
        related=related,
        categories=categories,
        link_title=False,
        active_nav="today",
        top_bar_date=top_bar_date,
        root_path="",
        css_path=f"static/style.css?v={css_version}",
    )

    with open(SITE_DIR / "index.html", "w") as f:
        f.write(html)
    print("  Generated: index.html")

    # 3. Generate archive page (always — needs the new entry)
    months = group_by_month(stories)
    template = env.get_template("archive.html")
    html = template.render(
        months=months,
        active_nav="archive",
        top_bar_date=top_bar_date,
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )

    with open(SITE_DIR / "archive" / "index.html", "w") as f:
        f.write(html)
    print(f"  Generated: archive/ ({len(stories)} stories)")

    # 4. Generate explore pages (always)
    template = env.get_template("explore.html")
    html = template.render(
        categories=categories,
        active_nav="explore",
        top_bar_date=top_bar_date,
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )

    with open(SITE_DIR / "explore" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: explore/")

    # Generate individual category pages
    template = env.get_template("explore_category.html")
    for cat_slug, cat_data in impact_map.items():
        cat_dir = SITE_DIR / "explore" / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)

        html = template.render(
            category=cat_data,
            stories=cat_data["stories"],
            active_nav="explore",
            top_bar_date=top_bar_date,
            root_path="../../",
            css_path=f"../../static/style.css?v={css_version}",
        )

        with open(cat_dir / "index.html", "w") as f:
            f.write(html)
        print(f"  Generated: explore/{cat_slug}/ ({cat_data['count']} stories)")

    # 5. Generate about page (always)
    template = env.get_template("about.html")
    html = template.render(
        active_nav="about",
        top_bar_date=top_bar_date,
        root_path="../",
        css_path=f"../static/style.css?v={css_version}",
    )

    with open(SITE_DIR / "about" / "index.html", "w") as f:
        f.write(html)
    print("  Generated: about/")

    print()
    print(f"Done. {generated} new story page(s) generated.")
    print(f"Site ready at: {SITE_DIR}/")


if __name__ == "__main__":
    full = "--full" in sys.argv
    if full:
        print("Full rebuild...")
    else:
        print("Incremental build...")
    print()
    generate(full_rebuild=full)
