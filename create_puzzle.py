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
    "date": today,
    "categories": [
        {
            "name": "Popular EV models in India",
            "bg": "#2171B5",
            "text": "#ffffff",
            "emoji": "🟦",
            "difficulty": 1,
            "items": ["Nexon", "Tigor", "Comet", "Ioniq5"]
        },
        {
            "name": "Types of Pollution",
            "bg": "#4CAF50",
            "text": "#ffffff",
            "emoji": "🟩",
            "difficulty": 2,
            "items": ["Air", "Water", "Light", "Noise"]
        },
        {
            "name": "Non-car (and climate friendly) ways of getting around!",
            "bg": "#FF8C00",
            "text": "#ffffff",
            "emoji": "🟧",
            "difficulty": 3,
            "items": ["Train", "Bus", "Cycle", "Metro"]
        },
        {
            "name": "Fuels that come from Petroleum (oil)",
            "bg": "#8B4513",
            "text": "#ffffff",
            "emoji": "🟫",
            "difficulty": 4,
            "items": ["Petrol", "Diesel", "Kerosene", "LPG"]
        }
    ]
}

def save_puzzle_to_archive(puzzle):
    """Save puzzle to archive folder."""
    date = puzzle["date"]
    filepath = f"torchlight-puzzles/{date}.json"

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
