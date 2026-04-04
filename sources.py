import logging
import re
import time
from datetime import datetime
from time import mktime
from urllib.parse import quote_plus

import feedparser
import requests
from bs4 import BeautifulSoup

from config import (
    GOOGLE_NEWS_BASE_URL,
    GOOGLE_NEWS_DELAY,
    GOOGLE_NEWS_QUERIES,
    REQUEST_TIMEOUT,
    USER_AGENT,
)

logger = logging.getLogger(__name__)


def fetch_rss(source):
    """Fetch articles from a single RSS source. Returns list of article dicts."""
    name = source["name"]
    url = source["url"]
    logger.info(f"Fetching RSS: {name} from {url}")

    try:
        feed = feedparser.parse(url, agent=USER_AGENT)

        if feed.bozo and not feed.entries:
            logger.warning(f"Feed error for {name}: {feed.bozo_exception}")
            return []

        articles = []
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue

            published_date = _parse_feed_date(entry)
            summary = _clean_summary(entry)

            articles.append({
                "title": title,
                "url": link,
                "source": name,
                "published_date": published_date,
                "summary": summary,
            })

        logger.info(f"Fetched {len(articles)} articles from {name}")
        return articles

    except Exception as e:
        logger.error(f"Failed to fetch {name}: {e}")
        return []


def fetch_google_news():
    """Fetch articles from Google News RSS for all configured queries."""
    all_articles = []

    for query in GOOGLE_NEWS_QUERIES:
        url = GOOGLE_NEWS_BASE_URL.format(query=quote_plus(query))
        logger.info(f"Fetching Google News: '{query}'")

        try:
            feed = feedparser.parse(url, agent=USER_AGENT)

            if feed.bozo and not feed.entries:
                logger.warning(f"Google News feed error for '{query}': {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if not title or not link:
                    continue

                # Google News source tag (e.g., "The Hindu")
                gn_source = ""
                if hasattr(entry, "source") and hasattr(entry.source, "title"):
                    gn_source = entry.source.title

                # Strip " - Publisher" suffix from title
                clean_title = _strip_source_suffix(title)

                published_date = _parse_feed_date(entry)
                summary = _clean_summary(entry)

                all_articles.append({
                    "title": clean_title,
                    "url": link,
                    "source": f"Google News ({gn_source})" if gn_source else "Google News",
                    "published_date": published_date,
                    "summary": summary,
                })

            logger.info(f"Fetched {len(feed.entries)} articles for '{query}'")

        except Exception as e:
            logger.error(f"Failed to fetch Google News for '{query}': {e}")

        time.sleep(GOOGLE_NEWS_DELAY)

    logger.info(f"Total Google News articles: {len(all_articles)}")
    return all_articles


def scrape_scroll(source):
    """Scrape articles from Scroll.in tag pages."""
    name = source["name"]
    all_articles = []

    for url in source["urls"]:
        logger.info(f"Scraping: {name} from {url}")
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Find article links -- Scroll.in uses <a> tags linking to /article/ paths
            article_links = soup.find_all("a", href=lambda h: h and "/article/" in h)

            seen_urls = set()
            for link_tag in article_links:
                href = link_tag.get("href", "")
                if not href or href in seen_urls:
                    continue

                if href.startswith("/"):
                    href = "https://scroll.in" + href

                seen_urls.add(href)

                # Extract title from heading tags inside the link
                heading = link_tag.find(["h1", "h2", "h3", "h4"])
                title = heading.get_text(strip=True) if heading else link_tag.get_text(strip=True)

                if not title or len(title) < 10:
                    continue

                # Extract summary from longer paragraph text
                summary = ""
                for p in link_tag.find_all("p"):
                    text = p.get_text(strip=True)
                    if len(text) > 30:
                        summary = text
                        break

                # Extract date from text content
                published_date = ""
                date_text = link_tag.get_text()
                date_match = re.search(
                    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}",
                    date_text,
                )
                if date_match:
                    try:
                        dt = datetime.strptime(date_match.group(), "%b %d, %Y")
                        published_date = dt.strftime("%Y-%m-%d")
                    except ValueError:
                        pass

                all_articles.append({
                    "title": title,
                    "url": href,
                    "source": name,
                    "published_date": published_date,
                    "summary": summary,
                })

            logger.info(f"Scraped {len(seen_urls)} articles from {url}")

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")

    return all_articles


def _parse_feed_date(entry):
    """Extract published date from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                dt = datetime.fromtimestamp(mktime(parsed))
                return dt.strftime("%Y-%m-%d")
            except (ValueError, OverflowError):
                continue
    return ""


def _clean_summary(entry):
    """Extract and clean summary text from a feedparser entry."""
    summary = entry.get("summary", entry.get("description", "")).strip()
    if "<" in summary:
        summary = BeautifulSoup(summary, "html.parser").get_text(separator=" ").strip()
    if len(summary) > 500:
        summary = summary[:497] + "..."
    return summary


def _strip_source_suffix(title):
    """Remove the ' - Source Name' suffix that Google News appends to titles."""
    # Google News titles end with " - Publisher Name"
    match = re.match(r"^(.+)\s+-\s+\S.*$", title)
    if match:
        return match.group(1).strip()
    return title
