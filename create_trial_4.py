#!/usr/bin/env python3
"""
Create and save a daily Trial-4 puzzle.
Usage: python3 create_trial_4.py
"""

import json
from datetime import datetime, timedelta

# Get tomorrow's date (April 11)
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

# Define the puzzle for Trial-4
PUZZLE = {
    "date": tomorrow,
    "categories": [
        {
            "name": "Express trains — Great alternatives to flying!",
            "bg": "#C8602A",
            "text": "#ffffff",
            "emoji": "🚆",
            "difficulty": 1,
            "items": ["Shatabdi", "Duronto", "Rajdhani", "Vande bharat"]
        },
        {
            "name": "Ticket status",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "emoji": "🎫",
            "difficulty": 2,
            "items": ["Waiting", "Confirmed", "Cancelled", "RAC"]
        },
        {
            "name": "Types of coaches in a train",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "emoji": "🚂",
            "difficulty": 3,
            "items": ["Sleeper", "General", "Pantry", "AC 3 tier"]
        },
        {
            "name": "Fields on a train ticket",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "emoji": "📋",
            "difficulty": 4,
            "items": ["PNR", "Name", "Status", "Train name"]
        }
    ]
}

def save_puzzle_to_archive(puzzle):
    """Save puzzle to archive folder."""
    date = puzzle["date"]
    filepath = f"trial-puzzles-4/{date}.json"

    with open(filepath, 'w') as f:
        json.dump(puzzle, f, indent=2)

    print(f"✅ Trial-4 puzzle saved: {filepath}")

def main():
    """Create and save the daily puzzle."""
    print(f"\n🧪 Creating Trial-4 puzzle for {PUZZLE['date']}\n")

    # Save to archive
    save_puzzle_to_archive(PUZZLE)

    print(f"📋 Categories:")
    for i, cat in enumerate(PUZZLE['categories'], 1):
        print(f"  {i}. {cat['name']}")
        print(f"     Items: {', '.join(cat['items'])}")

    print(f"\n⚠️  NEXT STEP: Update docs/trial-4/index.html with the PUZZLE data\n")

if __name__ == "__main__":
    main()
