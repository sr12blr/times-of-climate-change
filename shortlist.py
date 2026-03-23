#!/usr/bin/env python3
"""
Article Shortlister -- Scores and ranks climate news articles for general audience appeal.
Run: python3 shortlist.py [YYYY-MM-DD]
If no date given, uses today's date.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from config import DATA_DIR

# ---------------------------------------------------------------------------
# Scoring keywords
# ---------------------------------------------------------------------------

# Relatability: topics ordinary people care about (health, money, food, daily life)
HEALTH_KEYWORDS = [
    "cancer", "lung", "asthma", "disease", "hospital", "death", "risk",
    "health", "toxic", "drinking water", "contamination", "respiratory",
    "mortality", "illness", "medical", "doctor", "patient", "child",
    "children", "pregnant", "birth defect", "life expectancy", "aiims",
]

MONEY_KEYWORDS = [
    "price", "cost", "bill", "tax", "invest", "crore", "lakh", "rupee",
    "salary", "job", "jobs", "employment", "economy", "gdp", "subsidy",
    "tariff", "inflation", "expensive", "cheap", "afford", "trillion",
    "billion", "million", "budget", "revenue", "profit", "loss",
]

FOOD_KEYWORDS = [
    "crop", "farm", "farmer", "food", "water", "rice", "wheat", "milk",
    "vegetable", "fruit", "fish", "fishing", "agriculture", "harvest",
    "drought", "famine", "hunger", "irrigation", "groundwater", "drinking",
    "coffee", "tea", "spice",
]

DAILY_LIFE_KEYWORDS = [
    "commute", "transport", "bus", "metro", "traffic", "train", "auto",
    "school", "home", "house", "electricity", "power cut", "blackout",
    "water supply", "petrol", "diesel", "gas", "lpg", "cooking",
    "air quality", "breathe", "summer", "winter", "monsoon",
]

WEATHER_FEEL_KEYWORDS = [
    "heat wave", "heatwave", "flood", "cyclone", "rain", "temperature",
    "degrees", "celsius", "scorching", "sweltering", "freezing",
    "downpour", "storm", "thunder", "lightning", "humidity",
    "unprecedented rain", "coldest", "hottest", "warmest",
]

# Attention-catching: patterns that make people click/share
SURPRISE_KEYWORDS = [
    "first time", "first ever", "record", "highest", "lowest",
    "unprecedented", "never before", "historic", "shocking", "alarming",
    "surprising", "unexpected", "despite", "paradox", "ironic",
    "bizarre", "mystery", "secret", "hidden", "revealed",
    "breakthrough", "milestone", "landmark",
]

VIVID_KEYWORDS = [
    "dead", "killed", "collapsed", "disappeared", "vanished", "exploded",
    "burning", "sinking", "choking", "starving", "stranded", "rescued",
    "plastic", "garbage", "sewage", "smog", "wildfire", "inferno",
    "glacier melting", "species extinct", "forest fire",
]

# Scale/impact: affects many people
SCALE_KEYWORDS = [
    "national", "country", "across india", "all states", "nationwide",
    "million", "crore", "lakh", "population", "everyone", "all indians",
    "entire", "massive", "widespread", "pan-india",
]

MAJOR_CITIES = [
    "delhi", "mumbai", "bengaluru", "bangalore", "chennai", "kolkata",
    "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow", "kanpur",
    "nagpur", "visakhapatnam", "bhopal", "patna", "gurgaon", "noida",
    "ncr",
]

POLICY_KEYWORDS = [
    "government", "ministry", "supreme court", "high court", "ngt",
    "policy", "ban", "mandate", "regulation", "law", "act", "order",
    "directive", "guideline", "notification", "penalty", "fine",
    "parliament", "lok sabha", "rajya sabha",
]

# High-credibility sources (small boost)
TOP_SOURCES = [
    "the hindu", "indian express", "ndtv", "bbc", "the guardian",
    "scroll.in", "mongabay india", "down to earth", "india today",
    "the times of india", "hindustan times", "the wire",
    "indiaspend", "the economic times", "mint",
]


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def _count_keyword_hits(text, keyword_lists):
    """Count how many distinct keyword categories have at least one hit."""
    text_lower = text.lower()
    hits = 0
    matched = []
    for keywords in keyword_lists:
        for kw in keywords:
            if kw in text_lower:
                hits += 1
                matched.append(kw)
                break  # one hit per category is enough
    return hits, matched


def _keyword_score(text, keywords):
    """Count how many keywords from a single list match."""
    text_lower = text.lower()
    matches = [kw for kw in keywords if kw in text_lower]
    return len(matches), matches


def score_big_story(article, topic_clusters):
    """Score 0-20: Is this a big story covered by multiple sources?"""
    title_lower = " ".join(article["title"].lower().split())
    cluster_size = topic_clusters.get(title_lower, 1)

    if cluster_size >= 6:
        score = 20
    elif cluster_size >= 4:
        score = 16
    elif cluster_size >= 3:
        score = 12
    elif cluster_size >= 2:
        score = 8
    else:
        score = 0

    reason = f"{cluster_size} source(s) covering this topic" if cluster_size > 1 else ""
    return score, reason


def score_relatability(article):
    """Score 0-20: Is this relatable to common people?"""
    text = f"{article['title']} {article['summary']}"

    categories_hit, matched = _count_keyword_hits(text, [
        HEALTH_KEYWORDS, MONEY_KEYWORDS, FOOD_KEYWORDS,
        DAILY_LIFE_KEYWORDS, WEATHER_FEEL_KEYWORDS,
    ])

    # 0 categories = 0, 1 = 8, 2 = 14, 3 = 17, 4+ = 20
    score_map = {0: 0, 1: 8, 2: 14, 3: 17, 4: 20, 5: 20}
    score = score_map.get(categories_hit, 20)

    reason = f"Touches: {', '.join(matched[:4])}" if matched else ""
    return score, reason


def score_scale(article):
    """Score 0-15: Does this affect a large population?"""
    text = f"{article['title']} {article['summary']}"
    text_lower = text.lower()

    points = 0
    reasons = []

    # Major city mentioned
    cities_hit = [c for c in MAJOR_CITIES if c in text_lower]
    if cities_hit:
        points += 5
        reasons.append(f"Affects: {', '.join(cities_hit[:2])}")

    # National scale
    scale_hits, _ = _keyword_score(text_lower, SCALE_KEYWORDS)
    if scale_hits > 0:
        points += 5
        reasons.append("National scale")

    # Policy/government action
    policy_hits, _ = _keyword_score(text_lower, POLICY_KEYWORDS)
    if policy_hits > 0:
        points += 5
        reasons.append("Policy/govt action")

    return min(points, 15), "; ".join(reasons)


def score_attention(article):
    """Score 0-10: Is there something attention-catching?"""
    text = f"{article['title']} {article['summary']}"
    title = article["title"]

    points = 0
    reasons = []

    # Surprise/record/first
    surprise_hits, surprise_matched = _keyword_score(text, SURPRISE_KEYWORDS)
    if surprise_hits > 0:
        points += 4
        reasons.append(f"Surprise: {surprise_matched[0]}")

    # Vivid imagery
    vivid_hits, vivid_matched = _keyword_score(text, VIVID_KEYWORDS)
    if vivid_hits > 0:
        points += 3
        reasons.append(f"Vivid: {vivid_matched[0]}")

    # Question in title (curiosity gap)
    if "?" in title:
        points += 2
        reasons.append("Question headline")

    # Numbers/stats in title (specificity catches attention)
    if re.search(r"\d+%|\d+\s*(crore|lakh|million|billion|gw|mw)", title.lower()):
        points += 1
        reasons.append("Specific numbers")

    return min(points, 10), "; ".join(reasons)


def score_why_care(article):
    """Score 0-15: Strong 'why should you care' angle?"""
    text = f"{article['title']} {article['summary']}"

    points = 0
    reasons = []

    # Health risk angle
    health_hits, _ = _keyword_score(text, HEALTH_KEYWORDS)
    if health_hits >= 2:
        points += 7
        reasons.append("Health risk angle")
    elif health_hits == 1:
        points += 4
        reasons.append("Health mention")

    # Cost/money angle
    money_hits, _ = _keyword_score(text, MONEY_KEYWORDS)
    if money_hits >= 2:
        points += 5
        reasons.append("Money/cost angle")
    elif money_hits == 1:
        points += 3
        reasons.append("Money mention")

    # Direct weather impact
    weather_hits, _ = _keyword_score(text, WEATHER_FEEL_KEYWORDS)
    if weather_hits >= 2:
        points += 5
        reasons.append("Weather you feel")
    elif weather_hits == 1:
        points += 3

    return min(points, 15), "; ".join(reasons)


def score_source(article):
    """Score 0-20: Source credibility boost."""
    source_lower = article["source"].lower()

    # Check if the source (or Google News sub-source) matches a top source
    for top in TOP_SOURCES:
        if top in source_lower:
            return 20, f"Top source: {top.title()}"

    # Known but not top-tier sources
    mid_sources = [
        "business standard", "deccan herald", "news18", "tribune",
        "the economic times", "devdiscourse", "etv bharat",
    ]
    for mid in mid_sources:
        if mid in source_lower:
            return 12, f"Established source: {mid.title()}"

    # Other sources get base credit
    return 5, ""


# ---------------------------------------------------------------------------
# Topic clustering (detect "big stories")
# ---------------------------------------------------------------------------

def _extract_key_words(title):
    """Extract significant words from a title for topic matching."""
    stop_words = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "is", "are",
        "was", "were", "be", "been", "by", "with", "from", "as", "it", "its",
        "and", "or", "but", "not", "no", "how", "why", "what", "when", "where",
        "who", "which", "that", "this", "will", "can", "may", "has", "have",
        "had", "do", "does", "did", "new", "says", "said", "over", "after",
        "india", "indian", "s", "also", "more", "set", "get", "per", "now",
    }
    words = re.findall(r"[a-z]+", title.lower())
    return set(w for w in words if w not in stop_words and len(w) > 2)


def _extract_bigrams(title):
    """Extract 2-word phrases for better topic matching."""
    stop_words = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "is",
                  "are", "and", "or", "by", "with", "from", "as", "its", "s"}
    words = [w for w in re.findall(r"[a-z]+", title.lower())
             if w not in stop_words and len(w) > 2]
    return set(f"{words[i]} {words[i+1]}" for i in range(len(words) - 1))


def _extract_entities(text):
    """Extract proper nouns, acronyms, and numbers that identify specific events."""
    text_combined = f"{text}"
    # Acronyms (2+ uppercase letters): NTPC, CPCB, BMTC, IMD, etc.
    acronyms = set(re.findall(r"\b[A-Z]{2,}\b", text_combined))
    # Numbers with units (100 GW, 346 GWh, ₹7.9 trillion, 2.38 lakh)
    numbers = set(re.findall(r"\d+[\d.,]*\s*(?:gw|mw|gwh|crore|lakh|trillion|billion|million|%)", text_combined.lower()))
    # Proper nouns (capitalized words that aren't at sentence start) - simplified
    return acronyms | numbers


def _are_similar(words_i, words_j, bigrams_i, bigrams_j, entities_i, entities_j):
    """Check if two articles cover the same topic using multiple signals."""
    # 1. Jaccard similarity on key words (lowered threshold)
    if words_i and words_j:
        overlap = len(words_i & words_j)
        union = len(words_i | words_j)
        if union > 0 and overlap / union >= 0.3:
            return True

    # 2. Shared bigrams (strong signal — even 1 shared bigram is meaningful)
    if bigrams_i and bigrams_j:
        shared_bigrams = bigrams_i & bigrams_j
        if len(shared_bigrams) >= 1:
            return True

    # 3. Shared specific entities (acronyms + numbers = same event)
    if entities_i and entities_j:
        shared_entities = entities_i & entities_j
        # Need both a shared entity AND some word overlap
        word_overlap = len(words_i & words_j) if words_i and words_j else 0
        if len(shared_entities) >= 1 and word_overlap >= 2:
            return True

    return False


def build_topic_clusters(articles):
    """Group articles by topic similarity. Returns {normalized_title: cluster_size}.

    Uses multiple matching strategies:
    - Jaccard word similarity (threshold 0.3)
    - Bigram matching (shared 2-word phrases)
    - Entity matching (shared acronyms + numbers with word overlap)
    """
    article_data = []
    for a in articles:
        norm_title = " ".join(a["title"].lower().split())
        text = f"{a['title']} {a.get('summary', '')}"
        words = _extract_key_words(a["title"])
        bigrams = _extract_bigrams(a["title"])
        entities = _extract_entities(text)
        source = a["source"].split(" (")[0]
        article_data.append((norm_title, words, bigrams, entities, source))

    clusters = {}

    for i, (title_i, words_i, bigrams_i, entities_i, source_i) in enumerate(article_data):
        if not words_i:
            clusters[title_i] = 1
            continue

        similar_sources = {source_i}
        for j, (title_j, words_j, bigrams_j, entities_j, source_j) in enumerate(article_data):
            if i == j or not words_j:
                continue
            if _are_similar(words_i, words_j, bigrams_i, bigrams_j, entities_i, entities_j):
                similar_sources.add(source_j)

        clusters[title_i] = len(similar_sources)

    return clusters


# ---------------------------------------------------------------------------
# Main scoring pipeline
# ---------------------------------------------------------------------------

def score_article(article, topic_clusters):
    """Score a single article across all criteria. Returns (total, breakdown)."""
    big, big_r = score_big_story(article, topic_clusters)
    rel, rel_r = score_relatability(article)
    scale, scale_r = score_scale(article)
    attn, attn_r = score_attention(article)
    care, care_r = score_why_care(article)
    src, src_r = score_source(article)

    total = big + rel + scale + attn + care + src

    breakdown = {
        "big_story": {"score": big, "max": 20, "reason": big_r},
        "relatability": {"score": rel, "max": 20, "reason": rel_r},
        "source": {"score": src, "max": 20, "reason": src_r},
        "scale_impact": {"score": scale, "max": 15, "reason": scale_r},
        "why_care": {"score": care, "max": 15, "reason": care_r},
        "attention": {"score": attn, "max": 10, "reason": attn_r},
    }

    return total, breakdown


def shortlist(date_str=None, top_n=10):
    """Load articles for a date, score them, return top N."""
    if date_str is None:
        date_str = date.today().isoformat()

    filepath = DATA_DIR / f"{date_str}.json"
    if not filepath.exists():
        print(f"No data file found for {date_str}")
        print(f"Expected: {filepath}")
        return []

    with open(filepath, "r") as f:
        articles = json.load(f)

    # Freshness filter: only score articles from the last 3 days
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    cutoff = target_date - timedelta(days=3)

    fresh_articles = []
    for a in articles:
        if not a["published_date"]:
            # Keep articles with no date (benefit of the doubt)
            fresh_articles.append(a)
        else:
            try:
                pub = datetime.strptime(a["published_date"], "%Y-%m-%d").date()
                if pub >= cutoff:
                    fresh_articles.append(a)
            except ValueError:
                fresh_articles.append(a)

    print(f"Total articles: {len(articles)} | Fresh (last 3 days): {len(fresh_articles)}")
    print()

    # Build topic clusters using ALL articles (for coverage detection),
    # but only score fresh ones
    topic_clusters = build_topic_clusters(articles)

    # Score only fresh articles
    scored = []
    for article in fresh_articles:
        total, breakdown = score_article(article, topic_clusters)
        scored.append((total, breakdown, article))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Print top N
    print("=" * 80)
    print(f"  TOP {top_n} SHORTLISTED ARTICLES FOR {date_str}")
    print("=" * 80)

    for rank, (total, breakdown, article) in enumerate(scored[:top_n], 1):
        print()
        print(f"  #{rank}  SCORE: {total}/100")
        print(f"  {'-' * 70}")
        print(f"  Title:  {article['title']}")
        print(f"  Source: {article['source']}")
        print(f"  Date:   {article['published_date']}")
        print(f"  URL:    {article['url'][:90]}")
        print()

        # Score breakdown
        for criteria, info in breakdown.items():
            label = criteria.replace("_", " ").title()
            bar = "#" * info["score"] + "." * (info["max"] - info["score"])
            reason = f"  ({info['reason']})" if info["reason"] else ""
            print(f"    {label:<16} [{bar}] {info['score']}/{info['max']}{reason}")

        # Summary preview
        if article["summary"]:
            summary = article["summary"][:200]
            if len(article["summary"]) > 200:
                summary += "..."
            print()
            print(f"    Summary: {summary}")

        print()
        print(f"  {'=' * 70}")

    return scored[:top_n]


if __name__ == "__main__":
    target_date = sys.argv[1] if len(sys.argv) > 1 else None
    shortlist(target_date)
