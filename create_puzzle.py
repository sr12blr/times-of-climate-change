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
    "date": "2026-04-17",
    "categories": [
        {
            "name": "Tiger subspecies",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["Sumatran", "Bengal", "Siberian", "Malayan"]
        },
        {
            "name": "Big cats",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["Leopard", "Puma", "Jaguar", "Lion"]
        },
        {
            "name": "Wildlife tracking methods",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Radio collar", "DNA", "Camera traps", "Pug marks"]
        },
        {
            "name": "Things with stripes",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["Watermelon", "Barcode", "Zebra", "Tiger"]
        }
    ],
    "fun_fact": "India is home to about 75% of the world's wild tigers — but they're increasingly boxed in. Mining, roads and encroachments fragment their habitat into isolated pockets. Without wildlife corridors connecting these patches, tigers can't roam, hunt or find mates. Tracking methods like camera traps and pug marks help us monitor how many make it through.<br><br>Read: <a href=\"/story/lohardongri-iron-ore-mine-tiger-corridor-chandrapur/\" target=\"_blank\">When a mine threatens a tiger corridor →</a>",
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
