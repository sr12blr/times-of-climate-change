#!/usr/bin/env python3
"""
Climate News Collector -- Daily collection of India climate/environment news.
Run via cron or manually: python3 collect.py
"""

import json
import logging
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from config import (
    DATA_DIR,
    LOG_DIR,
    LOG_FILE,
    RSS_SOURCES,
    SCRAPE_SOURCES,
    INDIA_KEYWORDS,
    CLIMATE_KEYWORDS,
)
from sources import fetch_rss, fetch_google_news, scrape_scroll
from filters import filter_articles, deduplicate, filter_by_age


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stderr),
        ],
    )


def load_existing_urls(filepath):
    """Load article URLs from an existing JSON file (for re-run safety)."""
    if not filepath.exists():
        return set()
    try:
        with open(filepath, "r") as f:
            existing = json.load(f)
        return {a["url"] for a in existing}
    except (json.JSONDecodeError, KeyError):
        return set()


def load_previous_days(data_dir, today_str, lookback_days=7):
    """Load normalized URLs and titles from previous days' JSON files.

    Returns (set of normalized URLs, set of normalized titles).
    Used to avoid collecting duplicate articles across days.
    """
    from datetime import datetime, timedelta
    from urllib.parse import urlparse

    seen_urls = set()
    seen_titles = set()
    today = datetime.strptime(today_str, "%Y-%m-%d").date()

    for i in range(1, lookback_days + 1):
        past_date = (today - timedelta(days=i)).isoformat()
        past_file = data_dir / f"{past_date}.json"
        if not past_file.exists():
            continue
        try:
            with open(past_file, "r") as f:
                articles = json.load(f)
            for a in articles:
                parsed = urlparse(a["url"].rstrip("/"))
                norm_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
                seen_urls.add(norm_url)
                norm_title = " ".join(a["title"].lower().split())
                if norm_title:
                    seen_titles.add(norm_title)
        except (json.JSONDecodeError, KeyError):
            continue

    return seen_urls, seen_titles


def main():
    setup_logging()
    logger = logging.getLogger("collect")
    logger.info("=== Starting daily collection ===")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    output_file = DATA_DIR / f"{today}.json"

    all_articles = []

    # 1. RSS sources
    for source in RSS_SOURCES:
        articles = fetch_rss(source)
        articles = filter_articles(articles, source, INDIA_KEYWORDS, CLIMATE_KEYWORDS)
        all_articles.extend(articles)
        logger.info(f"{source['name']}: {len(articles)} articles after filtering")

    # 2. Google News
    google_config = {"name": "Google News", "needs_india_filter": False, "needs_climate_filter": False}
    gn_articles = fetch_google_news()
    gn_articles = filter_articles(gn_articles, google_config, INDIA_KEYWORDS, CLIMATE_KEYWORDS)
    all_articles.extend(gn_articles)
    logger.info(f"Google News: {len(gn_articles)} articles after filtering")

    # 3. Scrape sources
    for source in SCRAPE_SOURCES:
        articles = scrape_scroll(source)
        articles = filter_articles(articles, source, INDIA_KEYWORDS, CLIMATE_KEYWORDS)
        all_articles.extend(articles)
        logger.info(f"{source['name']}: {len(articles)} articles after filtering")

    # 4. Deduplicate across all sources (within today)
    all_articles = deduplicate(all_articles)

    # 4b. Drop stale articles (older than 5 days)
    all_articles = filter_by_age(all_articles, max_age_days=5)

    # 5. Remove articles already seen in previous days
    prev_urls, prev_titles = load_previous_days(DATA_DIR, today)
    before_cross_dedup = len(all_articles)
    all_articles = [
        a for a in all_articles
        if (
            f"{urlparse(a['url'].rstrip('/')).scheme}://{urlparse(a['url'].rstrip('/')).netloc}{urlparse(a['url'].rstrip('/')).path}".rstrip("/") not in prev_urls
            and " ".join(a["title"].lower().split()) not in prev_titles
        )
    ]
    cross_removed = before_cross_dedup - len(all_articles)
    if cross_removed > 0:
        logger.info(f"Cross-day dedup: removed {cross_removed} articles already seen in previous days")

    # 6. Handle re-runs: merge with existing file
    existing_urls = load_existing_urls(output_file)
    if existing_urls:
        new_articles = [a for a in all_articles if a["url"] not in existing_urls]
        logger.info(f"Re-run detected: {len(new_articles)} new articles to add")
        with open(output_file, "r") as f:
            existing_articles = json.load(f)
        existing_articles.extend(new_articles)
        all_articles = existing_articles

    # 7. Write output
    with open(output_file, "w") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(all_articles)} articles to {output_file}")
    logger.info("=== Collection complete ===")


if __name__ == "__main__":
    main()
