#!/usr/bin/env python3
"""
Create and save a daily Torchlight puzzle.
Usage: python3 create_puzzle.py

This script:
1. Saves the puzzle to the archive folder (torchlight-puzzles/YYYY-MM-DD.json)
2. Prints instructions for updating the game
"""

import json
from datetime import datetime

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Define the puzzle
PUZZLE = {
    "date": "2026-04-16",
    "categories": [
        {
            "name": "Quick _____",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["Commerce", "Fix", "Buck", "Question"]
        },
        {
            "name": "Things you'll read on a Q-comm app",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["Buy now", "50% off", "Free delivery above 99", "Offer ends in 10:59"]
        },
        {
            "name": "The backbone of Q-comm",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Dark stores", "Bike fleet", "Demand forecasting", "Gig workers"]
        },
        {
            "name": "The perils of Q-comm",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["Packaging waste", "Impulsive buys", "Accidents", "Poor working conditions"]
        }
    ],
    "fun_fact": "India's quick commerce market — Blinkit, Zepto, Swiggy Instamart — is growing at 40% a year. It's brought in unimaginable convenience, but at a huge cost — labour conditions, the environment and of course your own health and wallet!<br><br>Our favourite breakdown: <a href=\"https://www.newslaundry.com/2026/01/10/get-your-milton-friedman-and-ayn-rand-right-zomato-and-blinkit-arent-capitalism\" target=\"_blank\">What Q-comm really means (Newslaundry) →</a><br>Also read: <a href=\"https://sunnyclimatestormyclimate.substack.com/p/zen-and-the-art-of-living-without\" target=\"_blank\">Zen and the art of living without Blinkit →</a>",
    "author": "Sayesha D"
}

def save_puzzle_to_archive(puzzle):
    """Save puzzle to puzzles folder (read by generate_site.py)."""
    date = puzzle["date"]
    filepath = f"puzzles/{date}.json"

    with open(filepath, 'w') as f:
        json.dump(puzzle, f, indent=2)

    print(f"✅ Puzzle saved to archive: {filepath}")

def main():
    """Create and save the daily puzzle."""
    print(f"\n🔦 Creating Torchlight puzzle for {PUZZLE['date']}\n")

    # Save to archive
    save_puzzle_to_archive(PUZZLE)

    print(f"\n📋 Categories:")
    for i, cat in enumerate(PUZZLE['categories'], 1):
        print(f"  {i}. {cat['name']}")
        print(f"     Items: {', '.join(cat['items'])}")

    print(f"\n⚠️  NEXT STEP:")
    print(f"Run: python3 update_game.py")
    print(f"(or manually update the PUZZLE in docs/torchlight/index.html)\n")

if __name__ == "__main__":
    main()
