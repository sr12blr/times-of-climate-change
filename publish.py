#!/usr/bin/env python3
"""
Publish a daily climate story.

Usage:
    python3 publish.py create [YYYY-MM-DD]   # Create a story template to fill in
    python3 publish.py list                   # List all published stories

Creates a JSON file in stories/ that you edit with your story content.
Then run generate_site.py to rebuild the website.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

STORIES_DIR = Path(__file__).parent / "stories"


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].rstrip("-")


def create_story(date_str=None):
    """Create a story template JSON file for a given date."""
    if date_str is None:
        date_str = date.today().isoformat()

    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    story = {
        "date": date_str,
        "slug": "",
        "title": "",
        "what_talking_about": [
            "",
        ],
        "why_care": [
            "",
        ],
        "tags": [],
        "sources": [
            {"title": "", "url": ""},
        ],
        "related_stories": [],
    }

    filepath = STORIES_DIR / f"{date_str}.json"

    if filepath.exists():
        print(f"Story file already exists: {filepath}")
        print("Edit it directly or delete it first.")
        return

    with open(filepath, "w") as f:
        json.dump(story, f, indent=2, ensure_ascii=False)

    print(f"Created story template: {filepath}")
    print()
    print("Fill in the fields:")
    print("  - title: Your headline")
    print("  - slug: URL-friendly name (auto-generated from title if left empty)")
    print("  - what_talking_about: List of key highlights (bullet points)")
    print("  - why_care: List of 'why should you care' points")
    print("  - tags: List of tags like [\"Health\", \"ClimateChange\", \"HeatWave\"]")
    print("  - sources: List of {title, url} for source articles")
    print("  - related_stories: List of slugs from past stories (e.g. [\"story-slug\"])")
    print()
    print("Then run: python3 generate_site.py")


def list_stories():
    """List all published stories."""
    STORIES_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(STORIES_DIR.glob("*.json"), reverse=True)

    if not files:
        print("No stories published yet.")
        print("Run: python3 publish.py create")
        return

    print(f"Published stories ({len(files)}):")
    print()
    for f in files:
        try:
            with open(f, "r") as fh:
                story = json.load(fh)
            title = story.get("title", "(untitled)")
            tags = ", ".join(story.get("tags", []))
            print(f"  {story['date']}  {title}")
            if tags:
                print(f"             Tags: {tags}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  {f.name}  (error reading: {e})")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 publish.py create [YYYY-MM-DD]")
        print("  python3 publish.py list")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        d = sys.argv[2] if len(sys.argv) > 2 else None
        create_story(d)
    elif command == "list":
        list_stories()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
