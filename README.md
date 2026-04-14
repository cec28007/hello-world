# hello-world

## Florida vacant-land scraper

Two scrapers that search LandWatch for Florida lots that are **for sale**,
**bigger than 1 acre**, and **priced under $25,000**, then write the results
to a JSON file.

- **`scraper.py`** — plain `requests` + `BeautifulSoup`. Fast and
  light, but will fail if LandWatch's Cloudflare check flags your IP.
- **`scraper_playwright.py`** — drives a real headless Chromium browser,
  which passes the Cloudflare / PerimeterX bot-check. Slower but reliable.

Both produce the same output schema.

### Install — requests version

```
pip install -r requirements.txt
python scraper.py
```

### Install — Playwright version (recommended)

```
pip install -r requirements-playwright.txt
playwright install chromium
python scraper_playwright.py
```

### Common flags

```
--min-acres 1.0          # default
--max-price 25000        # default
--out florida_lots.json  # default output path
--quiet                  # suppress progress logs
```

Each entry in the output JSON has: `url`, `title`, `price`, `acres`,
`address`, `city`, `county`, `state`, `description`, `image`.

### Important caveats

- **LandWatch's Terms of Service prohibit automated scraping.** These
  scripts are provided for personal research only. Run them slowly and
  don't redistribute the scraped data.
- Both scrapers use 3–7 second random delays between pages.
- Listing markup changes over time. The parser first tries the embedded
  `application/ld+json` schema.org data (most stable), then falls back to
  CSS selectors. If both break, inspect a page's HTML and update
  `parse_listings()` in `scraper.py` — the Playwright variant reuses the
  same function.
