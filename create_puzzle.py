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
    "date": "2026-04-18",
    "categories": [
        {
            "name": "Car types",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["Petrol", "Diesel", "Hybrid", "Electric"]
        },
        {
            "name": "Benefits of EVs",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["No emissions", "Quiet", "Quick pick-up", "Fuel cost saving"]
        },
        {
            "name": "Concerns with EVs",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Range anxiety", "Upfront cost", "Battery degradation", "Resale value"]
        },
        {
            "name": "Problems with ALL cars",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["Traffic jams", "Parking", "Space hogger", "Accidents"]
        }
    ],
    "fun_fact": "India added over 1.5 mn EVs in 2025 — but 90% were 2Ws. Electric cars remain out of reach for most, due to high upfront costs and patchy charging infra. Meanwhile, the inconvenient truth: even the cleanest car causes traffic jams and takes up space meant for people.<br><br>Read: <a href=\"/story/delhi-ev-policy-registration-waiver-2028/\" target=\"_blank\">Delhi's EV push: what's actually changing →</a>",
    "author": ""
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
