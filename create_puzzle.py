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
            "name": "Have a monkey in the logo",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["Bira 91", "Mailchimp", "Monkey Shoulder", "Survey Monkey"]
        },
        {
            "name": "Have an owl in the logo",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["Duolingo", "TripAdvisor", "White Owl", "Chumbak"]
        },
        {
            "name": "Have a big cat in the logo",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Jaguar", "Puma", "King XI Punjab", "Govt of India"]
        },
        {
            "name": "Have a horse in the logo",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["US Polo", "Ferrari", "Hermes", "Porsche"]
        }
    ],
    "fun_fact": "So much of what we love — our brands, logos, even our language — is borrowed from the animal kingdom. Yet we're losing species at a staggering rate. Earth is currently in its Sixth Mass Extinction, with species disappearing up to 1,000 times faster than the natural background rate. And unlike the 5 extinctions before it, this one has a single cause: us.<br><br>Read: <a href=\"https://www.worldwildlife.org/resources/explainers/what-is-the-sixth-mass-extinction-and-what-can-we-do-about-it/\" target=\"_blank\">What is the sixth mass extinction and what can we do about it? →</a>",
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
