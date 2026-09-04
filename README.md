# World Cup Matches Dashboard

Interactive dashboard for cleaned FIFA World Cup match data from 1930 through 2022.

## What is included

- Match-level results and attendance
- Tournament trend summaries
- Team performance summaries
- Goal scorer rankings
- Venue summaries
- Data-quality checks

## Run locally

```bash
python scripts/build_dashboard.py
python -m http.server 4173 -d dist
```

Then open `http://127.0.0.1:4173`.

## Data

The cleaned CSV files are stored in the `data` folder. The dashboard is generated as a static HTML file in `dist/index.html`, so it can be hosted on GitHub Pages or any static web host.
