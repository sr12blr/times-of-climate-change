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
    "date": "2026-04-23",
    "categories": [
        {
            "name": "Benefits of Solar Energy",
            "bg": "#2C5F4A",
            "text": "#ffffff",
            "difficulty": 1,
            "description": "",
            "items": ["Renewable", "Clean", "Low_cost", "Decentralised"]
        },
        {
            "name": "Solar-Powered Appliances",
            "bg": "#1A5F7A",
            "text": "#ffffff",
            "difficulty": 2,
            "description": "",
            "items": ["Cooker", "Dryer", "Water_heater", "Pump"]
        },
        {
            "name": "Places to Install Solar Panels",
            "bg": "#C8602A",
            "text": "#ffffff",
            "difficulty": 3,
            "description": "",
            "items": ["Rooftop", "Agricultural_Fields", "Building_facade", "Canals"]
        },
        {
            "name": "Why Solar Panels May Underperform",
            "bg": "#6B1C2A",
            "text": "#ffffff",
            "difficulty": 4,
            "description": "",
            "items": ["Shade", "Heat", "Dust", "Poor_angle"]
        }
    ],
    "fun_fact": "India's solar capacity has grown over 30x in a decade — from under 3 GW in 2014 to over 120 GW today. With a national target of 500 GW of renewable energy by 2030, solar is critical to India's clean energy future.<br><br>Rooftop is a small but growing part of this. It lowers emissions AND your electricity bills all at once! See: <a href=\"https://www.youtube.com/watch?app=desktop&v=6434TVrhDHE&ra=m\" target=\"_blank\">How Rooftop Solar can change your life →</a>",
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
