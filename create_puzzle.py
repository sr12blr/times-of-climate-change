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
    "date": "2026-04-14",
    "categories": [
        {
            "name": "Varieties of Rice",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["Basmati", "Matta (Red rice)", "Jeera Samba", "Sona Masuri"]
        },
        {
            "name": "Varieties of Mango",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["Alphonso", "Kesar", "Dassheri", "Langda"]
        },
        {
            "name": "Varieties of Indian Chilis",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Bhoot Jolokia", "Guntur", "Kashmiri", "Bydagi"]
        },
        {
            "name": "Varieties of Banana",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["Nendran", "Elaichi/Yelakki", "Red banana", "Cavendish"]
        }
    ],
    "fun_fact": "India's crop diversity—from rice to bananas—isn't just tasty, it's climate-smart. Local varieties are adapted to their regions, resilient to weather shifts, and better for both your health and the environment."
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
