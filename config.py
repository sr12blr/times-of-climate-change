from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "collector.log"

# RSS feed sources
RSS_SOURCES = [
    {
        "name": "Mongabay India",
        "url": "https://india.mongabay.com/feed",
        "needs_india_filter": False,
        "needs_climate_filter": False,
    },
    {
        "name": "Down to Earth",
        "url": "https://www.downtoearth.org.in/feed",
        "needs_india_filter": False,
        "needs_climate_filter": False,
    },
    {
        "name": "The Hindu",
        "url": "https://www.thehindu.com/sci-tech/energy-and-environment/?service=rss",
        "needs_india_filter": False,
        "needs_climate_filter": False,
    },
    {
        "name": "Indian Express",
        "url": "https://indianexpress.com/section/climate-change/feed/",
        "needs_india_filter": False,
        "needs_climate_filter": False,
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/environment/climate-crisis/rss",
        "needs_india_filter": True,
        "needs_climate_filter": False,
    },
]

# Scrape sources (no RSS available)
SCRAPE_SOURCES = [
    {
        "name": "Scroll.in",
        "urls": [
            "https://scroll.in/tag/environment",
            "https://scroll.in/tag/climate-change",
        ],
        "needs_india_filter": False,
        "needs_climate_filter": False,
    },
]

# Google News RSS search queries (India locale)
GOOGLE_NEWS_QUERIES = [
    "climate change India",
    "renewable energy India",
    "environment India",
    "pollution India",
    "conservation India",
    "heat wave India",
    "extreme weather India",
    "plastic India",
    "public transport India",
]

GOOGLE_NEWS_BASE_URL = "https://news.google.com/rss/search?q={query}&hl=en&gl=IN&ceid=IN:en"
GOOGLE_NEWS_DELAY = 2  # seconds between requests

# Keywords for filtering (used for sources that need it)
INDIA_KEYWORDS = [
    "india", "indian", "delhi", "mumbai", "chennai", "kolkata",
    "bengaluru", "bangalore", "hyderabad", "kerala", "tamil nadu",
    "rajasthan", "gujarat", "maharashtra", "uttar pradesh",
    "madhya pradesh", "himalayas", "ganges", "ganga", "yamuna",
    "sundarbans", "western ghats", "modi", "ngt",
    "national green tribunal", "cpcb", "ministry of environment",
]

CLIMATE_KEYWORDS = [
    "climate", "environment", "pollution", "emission", "carbon",
    "global warming", "renewable", "solar", "wind energy", "flood",
    "drought", "deforestation", "biodiversity", "wildlife",
    "conservation", "air quality", "water crisis", "glacier",
    "sea level", "heatwave", "heat wave", "cyclone", "monsoon",
    "sustainable", "fossil fuel", "coal", "green energy",
    "electric vehicle", "ev", "forest", "ecosystem",
]

# Request settings
REQUEST_TIMEOUT = 30
USER_AGENT = "ClimateNewsCollector/1.0"
