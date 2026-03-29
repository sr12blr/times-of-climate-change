#!/usr/bin/env python3
"""Generate a WhatsApp channel cover image (HTML) for a story.

Usage:
    python3 generate_wa_cover.py                   # latest story
    python3 generate_wa_cover.py 2026-03-27        # specific date
    python3 generate_wa_cover.py --open             # open in browser after generating

The script produces wa_cover.html which you can screenshot at 1080x1080.
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STORIES_DIR = BASE_DIR / "stories"
IMAGES_DIR = BASE_DIR / "docs" / "static" / "images"
OUTPUT_FILE = BASE_DIR / "wa_cover.html"


def get_latest_story_date():
    files = sorted(STORIES_DIR.glob("*.json"))
    if not files:
        print("No stories found.")
        sys.exit(1)
    return files[-1].stem


def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%B %d, %Y").replace(" 0", " ")


def generate_cover(date_str):
    story_file = STORIES_DIR / f"{date_str}.json"
    if not story_file.exists():
        print(f"Story not found: {story_file}")
        sys.exit(1)

    with open(story_file) as f:
        story = json.load(f)

    title = story["title"]
    subtitle = story.get("subtitle", "")
    date_display = format_date(date_str)

    # Resolve image path
    image_html = ""
    if story.get("image"):
        img_path = IMAGES_DIR / os.path.basename(story["image"])
        if img_path.exists():
            image_html = f'<img src="file://{img_path}" alt="" class="cover-image">'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080">
<title>WA Cover — {date_str}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Source+Serif+4:wght@700&family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    width: 1080px;
    height: 1080px;
    overflow: hidden;
    background: #F8F8F6;
    font-family: 'Nunito Sans', sans-serif;
  }}

  .cover {{
    width: 1080px;
    height: 1080px;
    display: flex;
    flex-direction: column;
    position: relative;
  }}

  /* Top banner */
  .top-bar {{
    background: #1A1A18;
    padding: 36px 60px 32px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}

  .site-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 45px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.01em;
  }}

  .site-title em {{
    color: #D4380D;
    font-style: italic;
  }}

  .cover-date {{
    font-family: 'Nunito Sans', sans-serif;
    font-size: 32px;
    font-weight: 600;
    color: #aaaaaa;
    letter-spacing: 0.04em;
  }}

  /* Image section */
  .image-section {{
    flex: 1;
    overflow: hidden;
    position: relative;
    min-height: 0;
  }}

  .cover-image {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}

  /* No-image placeholder */
  .no-image {{
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #0E7C7B 0%, #2D6A1A 100%);
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .no-image span {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 120px;
    color: rgba(255,255,255,0.15);
  }}

  /* Gradient overlay on image for readability */
  .image-overlay {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(to bottom, rgba(26,26,24,0) 0%, rgba(26,26,24,0.95) 100%);
    pointer-events: none;
  }}

  /* Title section overlaid on bottom of image */
  .title-section {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0 60px 44px;
    z-index: 2;
  }}

  .story-title {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 56px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 12px;
  }}

  .story-subtitle {{
    font-family: 'Nunito Sans', sans-serif;
    font-size: 32px;
    font-style: italic;
    color: #FFD9B8;
    line-height: 1.45;
  }}

  /* Teal accent strip */
  .accent-strip {{
    height: 6px;
    background: #0E7C7B;
    flex-shrink: 0;
  }}

  /* Fallback: title below image when no image */
  .title-below {{
    padding: 40px 60px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

  .title-below .story-title {{
    color: #1A1A18;
    font-size: 52px;
  }}

  .title-below .story-subtitle {{
    color: #C8602A;
  }}
</style>
</head>
<body>
<div class="cover">
  <div class="top-bar">
    <div class="site-title">The Times of <em>Climate Change</em></div>
    <div class="cover-date">{date_display}</div>
  </div>
  <div class="accent-strip"></div>
"""

    if image_html:
        html += f"""  <div class="image-section">
    {image_html}
    <div class="image-overlay"></div>
    <div class="title-section">
      <div class="story-title">{title}</div>
      {"<div class='story-subtitle'>" + subtitle + "</div>" if subtitle else ""}
    </div>
  </div>
"""
    else:
        html += f"""  <div class="image-section">
    <div class="no-image"><span>&#127758;</span></div>
    <div class="image-overlay"></div>
    <div class="title-section">
      <div class="story-title">{title}</div>
      {"<div class='story-subtitle'>" + subtitle + "</div>" if subtitle else ""}
    </div>
  </div>
"""

    html += """</div>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

    print(f"Generated: {OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--open"]
    should_open = "--open" in sys.argv

    date_str = args[0] if args else get_latest_story_date()
    output = generate_cover(date_str)

    if should_open:
        subprocess.run(["open", str(output)])
