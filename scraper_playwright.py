"""
Playwright-based Florida vacant-land scraper.

Same filters and JSON output as ``scraper.py``, but drives a real headless
Chromium browser so LandWatch's Cloudflare / PerimeterX bot-check passes.

Install:
    pip install -r requirements-playwright.txt
    playwright install chromium

Run:
    python scraper_playwright.py                   # defaults: >1 ac, <$25k
    python scraper_playwright.py --max-price 20000
    python scraper_playwright.py --out results.json
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
from pathlib import Path

from playwright.async_api import (
    TimeoutError as PWTimeoutError,
    async_playwright,
)

# Reuse everything we already built for the requests-based scraper.
from scraper import (
    MAX_DELAY_SEC,
    MIN_DELAY_SEC,
    Listing,
    detect_last_page,
    page_urls,
    parse_listings,
    passes_filters,
    write_json,
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Max seconds to wait for a Cloudflare "Just a moment..." challenge to resolve.
CHALLENGE_WAIT_SEC = 30


async def _wait_past_challenge(page, *, verbose: bool) -> bool:
    """Return True if the page settled on real content, False if we gave up."""
    for _ in range(CHALLENGE_WAIT_SEC // 2):
        title = (await page.title()) or ""
        low = title.lower()
        if "just a moment" in low or "attention required" in low or "checking" in low:
            if verbose:
                print("  waiting on bot-check...", file=sys.stderr)
            await page.wait_for_timeout(2000)
            continue
        return True
    return False


async def fetch_html(page, url: str, *, verbose: bool) -> str | None:
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    except PWTimeoutError:
        if verbose:
            print(f"  navigation timeout: {url}", file=sys.stderr)
        return None

    if not await _wait_past_challenge(page, verbose=verbose):
        if verbose:
            print("  gave up waiting on bot-check", file=sys.stderr)
        return None

    # Let React hydrate listing cards / JSON-LD script tags.
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except PWTimeoutError:
        pass

    return await page.content()


async def scrape_async(
    min_acres: float, max_price: float, *, verbose: bool = True
) -> list[Listing]:
    results: dict[str, Listing] = {}
    last_page: int | None = None

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        page = await context.new_page()

        for i, url in enumerate(page_urls(min_acres, max_price), start=1):
            if last_page is not None and i > last_page:
                break
            if verbose:
                print(f"[page {i}] {url}", file=sys.stderr)

            html = await fetch_html(page, url, verbose=verbose)
            if html is None:
                break

            page_listings = parse_listings(html)
            if verbose:
                print(f"  parsed {len(page_listings)} listings", file=sys.stderr)
            if not page_listings:
                break

            new_on_page = 0
            for listing in page_listings:
                if listing.url in results:
                    continue
                if not passes_filters(listing, min_acres, max_price):
                    continue
                results[listing.url] = listing
                new_on_page += 1

            if new_on_page == 0 and i > 1:
                break

            if last_page is None:
                last_page = detect_last_page(html)
                if verbose and last_page:
                    print(f"  detected last page = {last_page}", file=sys.stderr)

            delay_ms = int(random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC) * 1000)
            await page.wait_for_timeout(delay_ms)

        await context.close()
        await browser.close()

    return list(results.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-acres", type=float, default=1.0)
    parser.add_argument("--max-price", type=float, default=25000.0)
    parser.add_argument("--out", type=Path, default=Path("florida_lots.json"))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    listings = asyncio.run(
        scrape_async(args.min_acres, args.max_price, verbose=not args.quiet)
    )
    write_json(listings, args.out)
    print(f"\nSaved {len(listings)} listings to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
