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
    "date": "2026-04-20",
    "categories": [
        {
            "name": "Signs of India's LPG crisis",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["4 wks for LPG", "Record sale of induction", "Long lines for CNG", "Reduced menus"]
        },
        {
            "name": "Raw material for Biogas",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["Animal manure", "Food waste", "Municipal sewage", "Crop residue"]
        },
        {
            "name": "Uses of Biogas",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Cooking", "Heating", "Transport fuel", "Industrial fuel"]
        },
        {
            "name": "Steps in Biogas supply chain",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["Waste segregation", "Collection", "Biogas plant", "Piped to kitchen"]
        }
    ],
    "fun_fact": "India has the ability to produce close to 62 million tonnes of biogas annually. But at present, we are tapping less than 1% of that. Biogas is a great solution — it gives us energy security, is cheaper and reduces emissions all at once!<br><br>Watch: <a href=\"https://www.youtube.com/watch?v=knHNXDCiiEg&t=308s\" target=\"_blank\">India NEEDS Biogas | Here's Why →</a>",
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
