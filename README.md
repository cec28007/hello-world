# hello-world

## Florida vacant-land scraper

`scraper.py` searches LandWatch for Florida lots that are **for sale**,
**bigger than 1 acre**, and **priced under $25,000**, then writes the results
to a JSON file.

### Install

```
pip install -r requirements.txt
```

### Run

```
python scraper.py                       # defaults: >1 acre, <$25,000 -> florida_lots.json
python scraper.py --max-price 20000     # cheaper cap
python scraper.py --min-acres 2.5       # bigger lots
python scraper.py --out results.json    # custom output path
```

Each entry in the output JSON has: `url`, `title`, `price`, `acres`,
`address`, `city`, `county`, `state`, `description`, `image`.

### Important caveats

- **LandWatch's Terms of Service prohibit automated scraping.** This script
  is provided for personal research only. Run it slowly and don't
  redistribute the scraped data.
- The script uses polite 3–7 second delays between pages and realistic
  browser headers, but LandWatch has aggressive bot protection. If you get
  HTTP 403 or a CAPTCHA page, plain `requests` won't work — you'll need to
  port the same logic to Playwright (headless browser).
- Listing markup changes over time. The parser first tries the embedded
  `application/ld+json` schema.org data (most stable), then falls back to
  CSS selectors. If both break, inspect a page's HTML and update
  `parse_listings()`.
