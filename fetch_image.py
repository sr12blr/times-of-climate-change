#!/usr/bin/env python3
"""
Fetch story images from Unsplash (primary) or Wikimedia Commons (fallback).

Usage:
    python3 fetch_image.py <story-slug> "<search query>"
    python3 fetch_image.py <story-slug> "<search query>" --save <index>
    python3 fetch_image.py <story-slug> --url "<image-url>"

Examples:
    # Search and preview options
    python3 fetch_image.py navi-mumbai-flamingo-lakes-toxic "flamingo mumbai lake"

    # Save option 2 from the last search
    python3 fetch_image.py navi-mumbai-flamingo-lakes-toxic "flamingo mumbai lake" --save 2

    # Use a direct URL
    python3 fetch_image.py navi-mumbai-flamingo-lakes-toxic --url "https://example.com/photo.jpg"
"""

import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent
STORIES_DIR = BASE_DIR / "stories"
IMAGES_DIR = BASE_DIR / "docs" / "static" / "images"
KEY_FILE = BASE_DIR / ".unsplash_key"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_unsplash_key():
    if not KEY_FILE.exists():
        print("Error: .unsplash_key file not found. Create it with your Unsplash access key.")
        sys.exit(1)
    return KEY_FILE.read_text().strip()


def search_unsplash(query, per_page=6):
    """Search Unsplash and return photo results."""
    key = get_unsplash_key()
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
    })
    url = f"https://api.unsplash.com/search/photos?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Client-ID {key}",
        "Accept-Version": "v1",
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data.get("results", [])


def search_wikimedia(query, limit=6):
    """Search Wikimedia Commons for freely licensed images."""
    params = urllib.parse.urlencode({
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrlimit": limit,
        "gsrnamespace": "6",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "iiurlwidth": 1200,
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "ClimateNewsSite/1.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    results = []
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo", [{}])[0]
        meta = info.get("extmetadata", {})
        results.append({
            "thumb_url": info.get("thumburl", ""),
            "full_url": info.get("url", ""),
            "download_url": info.get("thumburl", ""),  # Use the 1200px thumb
            "width": info.get("thumbwidth", 0),
            "height": info.get("thumbheight", 0),
            "description": meta.get("ImageDescription", {}).get("value", "")[:100],
            "author": meta.get("Artist", {}).get("value", "Unknown"),
            "license": meta.get("LicenseShortName", {}).get("value", "Unknown"),
            "source": "wikimedia",
            "page_url": f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(page.get('title', '').replace('File:', ''))}",
        })
    return results


def display_unsplash_results(results):
    """Display Unsplash search results for user review."""
    if not results:
        print("No Unsplash results found.")
        return
    print(f"\n{'='*60}")
    print(f"  UNSPLASH RESULTS ({len(results)} photos)")
    print(f"{'='*60}\n")
    for i, photo in enumerate(results, 1):
        user = photo.get("user", {}).get("name", "Unknown")
        desc = (photo.get("description") or photo.get("alt_description") or "No description")[:80]
        w = photo.get("width", 0)
        h = photo.get("height", 0)
        thumb = photo["urls"]["small"]
        print(f"  [{i}] {desc}")
        print(f"      By: {user} | {w}x{h}")
        print(f"      Preview: {thumb}")
        print()


def display_wikimedia_results(results):
    """Display Wikimedia search results for user review."""
    if not results:
        print("No Wikimedia results found.")
        return
    print(f"\n{'='*60}")
    print(f"  WIKIMEDIA COMMONS RESULTS ({len(results)} images)")
    print(f"{'='*60}\n")
    for i, img in enumerate(results, 1):
        desc = img["description"][:80] if img["description"] else "No description"
        print(f"  [{i}] {desc}")
        print(f"      By: {img['author'][:60]} | License: {img['license']}")
        print(f"      Preview: {img['thumb_url']}")
        print()


def download_image(url, slug, headers=None):
    """Download image and save as slug.jpg."""
    filepath = IMAGES_DIR / f"{slug}.jpg"
    req = urllib.request.Request(url)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    filepath.write_bytes(data)
    size_kb = len(data) / 1024
    print(f"\n  Saved: {filepath} ({size_kb:.0f} KB)")
    return filepath


def update_story_json(slug, image_path, credit=None, credit_url=None):
    """Add image field to story JSON."""
    story_files = list(STORIES_DIR.glob("*.json"))
    for f in story_files:
        try:
            with open(f) as fh:
                story = json.load(fh)
            if story.get("slug") == slug:
                story["image"] = f"static/images/{slug}.jpg"
                if credit:
                    story["image_credit"] = credit
                if credit_url:
                    story["image_credit_url"] = credit_url
                with open(f, "w") as fh:
                    json.dump(story, fh, indent=2, ensure_ascii=False)
                    fh.write("\n")
                print(f"  Updated: {f.name}")
                return True
        except (json.JSONDecodeError, KeyError):
            continue
    print(f"  Warning: No story found with slug '{slug}'")
    return False


def trigger_unsplash_download(photo):
    """Trigger Unsplash download endpoint (required by API guidelines)."""
    download_url = photo.get("links", {}).get("download_location")
    if download_url:
        key = get_unsplash_key()
        req = urllib.request.Request(
            f"{download_url}?client_id={key}",
            headers={"Accept-Version": "v1"},
        )
        try:
            urllib.request.urlopen(req)
        except Exception:
            pass  # Non-critical


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    slug = sys.argv[1]

    # Direct URL mode
    if sys.argv[2] == "--url":
        if len(sys.argv) < 4:
            print("Error: Provide a URL after --url")
            sys.exit(1)
        url = sys.argv[3]
        filepath = download_image(url, slug)
        update_story_json(slug, filepath)
        return

    query = sys.argv[2]

    # Save mode
    if "--save" in sys.argv:
        save_idx = int(sys.argv[sys.argv.index("--save") + 1])
        source = sys.argv[sys.argv.index("--save") + 2] if len(sys.argv) > sys.argv.index("--save") + 2 else "unsplash"

        if source == "unsplash":
            results = search_unsplash(query)
            if save_idx < 1 or save_idx > len(results):
                print(f"Error: Index {save_idx} out of range (1-{len(results)})")
                sys.exit(1)
            photo = results[save_idx - 1]
            # Use the "regular" size (1080px wide)
            img_url = photo["urls"]["regular"]
            user = photo["user"]
            trigger_unsplash_download(photo)
            filepath = download_image(img_url, slug)
            credit = user.get("name", "Unknown")
            credit_url = f"https://unsplash.com/@{user.get('username', '')}?utm_source=times_of_climate_change&utm_medium=referral"
            update_story_json(slug, filepath, credit=credit, credit_url=credit_url)
        elif source == "wikimedia":
            results = search_wikimedia(query)
            if save_idx < 1 or save_idx > len(results):
                print(f"Error: Index {save_idx} out of range (1-{len(results)})")
                sys.exit(1)
            img = results[save_idx - 1]
            filepath = download_image(img["download_url"], slug)
            update_story_json(slug, filepath, credit=img["author"][:60], credit_url=img["page_url"])
        return

    # Search mode — show results for review
    print(f"\nSearching for: \"{query}\" (slug: {slug})")

    # Try Unsplash first
    print("\n--- Unsplash ---")
    unsplash_results = search_unsplash(query)
    display_unsplash_results(unsplash_results)

    if not unsplash_results:
        # Fallback to Wikimedia
        print("\n--- Wikimedia Commons (fallback) ---")
        wiki_results = search_wikimedia(query)
        display_wikimedia_results(wiki_results)

    print(f"\nTo save an image, run:")
    print(f"  python3 fetch_image.py {slug} \"{query}\" --save <number>")
    if not unsplash_results:
        print(f"  python3 fetch_image.py {slug} \"{query}\" --save <number> wikimedia")


if __name__ == "__main__":
    main()
