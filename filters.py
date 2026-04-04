import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def matches_keywords(text, keywords):
    """Check if text contains any of the given keywords (case-insensitive)."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def filter_articles(articles, source_config, india_keywords, climate_keywords):
    """Apply keyword filters based on source configuration."""
    needs_india = source_config.get("needs_india_filter", False)
    needs_climate = source_config.get("needs_climate_filter", False)

    if not needs_india and not needs_climate:
        return articles

    filtered = []
    for article in articles:
        searchable = f"{article['title']} {article['summary']}"

        if needs_india and not matches_keywords(searchable, india_keywords):
            continue
        if needs_climate and not matches_keywords(searchable, climate_keywords):
            continue

        filtered.append(article)

    removed = len(articles) - len(filtered)
    if removed > 0:
        logger.info(f"Filtered out {removed} irrelevant articles from {source_config['name']}")

    return filtered


def deduplicate(articles):
    """Remove duplicate articles based on normalized URL and title.

    Uses both URL and title matching since Google News URLs differ from
    the original publisher URLs for the same article.
    """
    seen_urls = set()
    seen_titles = set()
    unique = []

    for article in articles:
        parsed = urlparse(article["url"].rstrip("/"))
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

        # Normalize title for comparison: lowercase, strip extra whitespace
        normalized_title = " ".join(article["title"].lower().split())

        if normalized_url in seen_urls:
            continue
        if normalized_title in seen_titles:
            continue

        seen_urls.add(normalized_url)
        if normalized_title:
            seen_titles.add(normalized_title)
        unique.append(article)

    removed = len(articles) - len(unique)
    if removed > 0:
        logger.info(f"Deduplicated: removed {removed} duplicate articles")

    return unique
