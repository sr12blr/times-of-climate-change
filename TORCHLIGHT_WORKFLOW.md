# Torchlight Daily Puzzle Workflow

## Overview
Create one climate-themed word puzzle per day for the Torchlight game.

## Daily Workflow

### Step 1: Create Puzzle (Morning)
Edit `/Users/sailee/climate-v2/create_puzzle.py` and update the `PUZZLE` variable with today's 4 categories and items:

```python
PUZZLE = {
    "date": "2026-04-09",  # Update this
    "categories": [
        {
            "name": "Category Name",
            "bg": "#COLOR",
            "text": "#COLOR",
            "emoji": "🟦",
            "difficulty": 1,
            "items": ["Item1", "Item2", "Item3", "Item4"]
        },
        # ... 4 categories total, difficulty 1-4
    ]
}
```

Run the script to save:
```bash
python3 create_puzzle.py
```

This saves to: `torchlight-puzzles/2026-04-09.json`

### Step 2: Update Game
Manually update the `PUZZLE` constant in `/Users/sailee/climate-v2/docs/torchlight/index.html` with the same data.

Also update the date:
```html
<div class="game-date">April 9, 2026</div>
```

### Step 3: Test & Deploy
```bash
# Test locally
python3 -m http.server 8081

# Then push to GitHub
git add -A
git commit -m "Torchlight: puzzle for 2026-04-09"
git push
```

---

## Puzzle Design Guidelines

### 1. Four Categories (Difficulty 1-4)
- **Difficulty 1** (Straightforward): Most obvious category
- **Difficulty 2** (Medium): Requires some thought
- **Difficulty 3** (Tricky): Lateral thinking needed
- **Difficulty 4** (Devious): Most challenging

### 2. Climate + India Focus
- Connect to daily life in India
- Food, water, air, energy, mobility themes
- Make connections that aren't immediately obvious

### 3. Colors (Don't Change)
```
Difficulty 1: #2171B5 (Blue) 🟦
Difficulty 2: #F5F5F5 (White) ⬜
Difficulty 3: #F4A582 (Orange) 🟧
Difficulty 4: #B2182B (Red) 🟥
```

### 4. Item Rules
- 4 items per category (16 total)
- All items should be exact matches for that category
- No items should fit multiple categories
- Single words preferred (use "_" for phrases like "Water sprinkler")

---

## Archive Structure
```
torchlight-puzzles/
├── 2026-04-08.json
├── 2026-04-09.json
└── ...
```

Each file contains complete puzzle data for that day.

---

## Example Puzzle (April 8, 2026)

**Category 1 — Types of Pollution** (Blue, Difficulty 1)
- Air, Water, Noise, Light

**Category 2 — Urban Transportation** (White, Difficulty 2)
- Bus, Train, Metro, Cycle

**Category 3 — Ways to Protect from Air Pollution** (Orange, Difficulty 3)
- Smog tower, Air purifier, Masks, Water sprinkler

**Category 4 — Crops Affected by Climate Change** (Red, Difficulty 4)
- Coffee, Cocoa, Rice, Olive oil

---

## Future: Automated Loading
Puzzles will eventually load dynamically from the archive folder based on the date, so you'll only need to create the JSON file.
