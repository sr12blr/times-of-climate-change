#!/usr/bin/env python3
"""
Create and save a daily Trial-2 puzzle.
Usage: python3 create_trial_2.py
"""

import json
from datetime import datetime

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Define the puzzle for Trial-2
PUZZLE = {
    "date": today,
    "categories": [
        {
            "name": "Types of fossil fuels",
            "bg": "#2171B5",
            "text": "#ffffff",
            "emoji": "🟦",
            "difficulty": 1,
            "items": ["Coal", "Oil", "Natural Gas", "Petroleum"]
        },
        {
            "name": "Migratory birds that visit India",
            "bg": "#F5F5F5",
            "text": "#1A1A18",
            "border": "#CCCCCC",
            "emoji": "⬜",
            "difficulty": 2,
            "items": ["Greater Flamingo", "Rosy Pelican", "Siberian Crane", "Amur Falcon"]
        },
        {
            "name": "Parts of IPL team names",
            "bg": "#F4A582",
            "text": "#1A1A18",
            "emoji": "🟧",
            "difficulty": 3,
            "items": ["Superkings", "Knight Riders", "Royals", "Super Giants"]
        },
        {
            "name": "New years festivals",
            "bg": "#B2182B",
            "text": "#ffffff",
            "emoji": "🟥",
            "difficulty": 4,
            "items": ["Gudi Padwa", "Ugadi", "Vishu", "Puthandu"]
        }
    ]
}

def save_puzzle_to_archive(puzzle):
    """Save puzzle to archive folder."""
    date = puzzle["date"]
    filepath = f"trial-puzzles-2/{date}.json"

    with open(filepath, 'w') as f:
        json.dump(puzzle, f, indent=2)

    print(f"✅ Trial-2 puzzle saved: {filepath}")

def main():
    """Create and save the daily puzzle."""
    print(f"\n🧪 Creating Trial-2 puzzle for {PUZZLE['date']}\n")

    # Save to archive
    save_puzzle_to_archive(PUZZLE)

    print(f"📋 Categories:")
    for i, cat in enumerate(PUZZLE['categories'], 1):
        print(f"  {i}. {cat['name']}")
        print(f"     Items: {', '.join(cat['items'])}")

    print(f"\n⚠️  NEXT STEP: Update docs/trial-2/index.html with the PUZZLE data\n")

if __name__ == "__main__":
    main()
