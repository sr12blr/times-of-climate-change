#!/usr/bin/env python3
"""
Create and save a daily Trial-3 puzzle.
Usage: python3 create_trial_3.py
"""

import json
from datetime import datetime, timedelta

# Get tomorrow's date (April 10)
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

# Define the puzzle for Trial-3
PUZZLE = {
    "date": tomorrow,
    "categories": [
        {
            "name": "Millets - need less water to grow!",
            "bg": "#2171B5",
            "text": "#ffffff",
            "emoji": "🟦",
            "difficulty": 1,
            "items": ["Ragi", "Bajra", "Jowar", "Sorghum"]
        },
        {
            "name": "Sugarcane products",
            "bg": "#F5F5F5",
            "text": "#1A1A18",
            "border": "#CCCCCC",
            "emoji": "⬜",
            "difficulty": 2,
            "items": ["Sugar", "Jaggery", "Molasses", "Ethanol"]
        },
        {
            "name": "Coconut ______",
            "bg": "#F4A582",
            "text": "#1A1A18",
            "emoji": "🟧",
            "difficulty": 3,
            "items": ["Oil", "Coir", "Water", "Milk"]
        },
        {
            "name": "Cash crops that are affected by climate change",
            "bg": "#B2182B",
            "text": "#ffffff",
            "emoji": "🟥",
            "difficulty": 4,
            "items": ["Coffee", "Cocoa", "Mango", "Olive"]
        }
    ]
}

def save_puzzle_to_archive(puzzle):
    """Save puzzle to archive folder."""
    date = puzzle["date"]
    filepath = f"trial-puzzles-3/{date}.json"

    with open(filepath, 'w') as f:
        json.dump(puzzle, f, indent=2)

    print(f"✅ Trial-3 puzzle saved: {filepath}")

def main():
    """Create and save the daily puzzle."""
    print(f"\n🧪 Creating Trial-3 puzzle for {PUZZLE['date']}\n")

    # Save to archive
    save_puzzle_to_archive(PUZZLE)

    print(f"📋 Categories:")
    for i, cat in enumerate(PUZZLE['categories'], 1):
        print(f"  {i}. {cat['name']}")
        print(f"     Items: {', '.join(cat['items'])}")

    print(f"\n⚠️  NEXT STEP: Update docs/trial-3/index.html with the PUZZLE data\n")

if __name__ == "__main__":
    main()
