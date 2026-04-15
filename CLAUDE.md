# Notes for Claude

## Torchlight Puzzle

Puzzle JSON files go in `puzzles/YYYY-MM-DD.json` — NOT `torchlight-puzzles/`.

The `torchlight-puzzles/` folder exists but is not read by `generate_site.py`. Always use `puzzles/`.

After creating the JSON, run `python3 generate_site.py` to regenerate `docs/torchlight/index.html`.
