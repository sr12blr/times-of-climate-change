# Trial Editions — Torchlight Experiments

Two independent puzzle editions for testing different themes and approaches.

## Quick Start (Local)

**Start dev server:**
```bash
python3 -m http.server 8081
```

**Access trials locally:**
- **Trial-1**: http://localhost:8081/trial-1/
- **Trial-2**: http://localhost:8081/trial-2/

---

## Trial-1: Classic Climate (India-focused)

**Theme**: Everyday climate impacts in India

**Puzzle Categories:**
1. Types of Pollution (Air, Water, Noise, Light)
2. Urban Transportation (Bus, Train, Metro, Cycle)
3. Ways to Protect from Air Pollution (Smog tower, Air purifier, Masks, Water sprinkler)
4. Crops Affected by Climate Change (Coffee, Cocoa, Rice, Olive oil)

**Archive**: `trial-puzzles-1/`
**Create puzzle**: `python3 create_trial_1.py`
**Game**: `docs/trial-1/index.html`

---

## Trial-2: Global Climate

**Theme**: Broader climate science and global impacts

**Puzzle Categories:**
1. Renewable Energy Sources (Solar, Wind, Hydro, Geothermal)
2. Climate Impacts on Food (Drought, Flood, Pest, Frost)
3. Carbon Reduction Methods (Reforestation, Energy efficiency, Electric vehicle, Plant-based diet)
4. Weather Patterns in India (Monsoon, Heat wave, Cold wave, Cyclone)

**Archive**: `trial-puzzles-2/`
**Create puzzle**: `python3 create_trial_2.py`
**Game**: `docs/trial-2/index.html`

---

## Deployment to Vercel

When ready to deploy:
```bash
vercel --prod
```

Both trials will be live at:
- `https://times-of-climate-change.vercel.app/trial-1/`
- `https://times-of-climate-change.vercel.app/trial-2/`

---

## File Structure

```
climate-v2/
├── docs/
│   ├── trial-1/          # Trial-1 game
│   └── trial-2/          # Trial-2 game
├── trial-puzzles-1/      # Trial-1 archive
├── trial-puzzles-2/      # Trial-2 archive
├── create_trial_1.py
└── create_trial_2.py
```
