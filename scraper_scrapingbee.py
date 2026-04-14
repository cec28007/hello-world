"""
ScrapingBee-backed Florida vacant-land scraper.

Uses the ScrapingBee API (https://www.scrapingbee.com/) to fetch pages,
which handles Akamai / Cloudflare / PerimeterX bot-checks for us. The
existing JSON-LD parser in scraper.py does the rest.

Setup:
    1. Sign up at https://www.scrapingbee.com (free tier = 1,000 credits)
    2. Copy your API key from the dashboard
    3. Put it in a .env file next to this script, one line:
           SCRAPINGBEE_API_KEY=your_key_here
       ...or export it:  export SCRAPINGBEE_API_KEY=your_key_here

Run:
    python scraper_scrapingbee.py                   # LandSearch, premium proxy
    python scraper_scrapingbee.py --site landwatch  # needs stealth proxy (75 credits/page)
    python scraper_scrapingbee.py --stealth         # force stealth proxy

Credit cost per page (approx):
    render_js=true + premium_proxy=true        -> 10 credits
    render_js=true + stealth_proxy=true        -> 75 credits

Free tier (1,000 credits) gets you ~100 premium pages or ~13 stealth pages.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path

import requests

from scraper import (
    DEFAULT_SITE,
    MAX_DELAY_SEC,
    MIN_DELAY_SEC,
    SITES,
    Listing,
    detect_last_page,
    page_urls,
    parse_listings,
    passes_filters,
    write_json,
)

SCRAPINGBEE_ENDPOINT = "https://app.scrapingbee.com/api/v1/"

# Sites that need the (expensive) stealth proxy. Others work fine with
# the plain premium proxy.
NEEDS_STEALTH = {"landwatch"}


def load_api_key() -> str:
    """Read SCRAPINGBEE_API_KEY from env, or from a .env file next to us."""
    key = os.environ.get("SCRAPINGBEE_API_KEY")
    if key:
        return key.strip()

    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "SCRAPINGBEE_API_KEY":
                return value.strip().strip('"').strip("'")

    print(
        "ERROR: SCRAPINGBEE_API_KEY is not set.\n"
        "  1. Sign up at https://www.scrapingbee.com (free 1,000 credits)\n"
        "  2. Copy your API key from the dashboard\n"
        f"  3. Create {env_path} containing: SCRAPINGBEE_API_KEY=<your key>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def fetch_via_scrapingbee(
    api_key: str, url: str, *, stealth: bool, verbose: bool = True
) -> str | None:
    params = {
        "api_key": api_key,
        "url": url,
        "render_js": "true",
        "country_code": "us",
        # Wait for the page to settle so JSON-LD script tags are present.
        "wait_browser": "networkidle2",
    }
    if stealth:
        params["stealth_proxy"] = "true"
    else:
        params["premium_proxy"] = "true"

    try:
        resp = requests.get(SCRAPINGBEE_ENDPOINT, params=params, timeout=180)
    except requests.RequestException as exc:
        if verbose:
            print(f"  scrapingbee network error: {exc}", file=sys.stderr)
        return None

    # Show remaining credits when the header is present.
    if verbose:
        remaining = resp.headers.get("Spb-Cost") or resp.headers.get("spb-cost")
        credits_left = (
            resp.headers.get("Spb-remaining-request-credits")
            or resp.headers.get("spb-remaining-request-credits")
        )
        if remaining or credits_left:
            print(
                f"  [scrapingbee] cost={remaining} remaining={credits_left}",
                file=sys.stderr,
            )

    if resp.status_code != 200:
        if verbose:
            print(
                f"  scrapingbee returned HTTP {resp.status_code}: "
                f"{resp.text[:300]}",
                file=sys.stderr,
            )
        return None

    return resp.text


def scrape(
    min_acres: float,
    max_price: float,
    *,
    site: str = DEFAULT_SITE,
    stealth: bool | None = None,
    verbose: bool = True,
) -> list[Listing]:
    api_key = load_api_key()

    if stealth is None:
        stealth = site in NEEDS_STEALTH

    if verbose:
        cost = 75 if stealth else 10
        print(
            f"==> site={site} stealth={stealth} (~{cost} credits/page)",
            file=sys.stderr,
        )

    results: dict[str, Listing] = {}
    last_page: int | None = None

    for i, url in enumerate(page_urls(min_acres, max_price, site), start=1):
        if last_page is not None and i > last_page:
            break
        if verbose:
            print(f"[page {i}] {url}", file=sys.stderr)

        html = fetch_via_scrapingbee(api_key, url, stealth=stealth, verbose=verbose)
        if html is None:
            break

        page_listings = parse_listings(html)
        if verbose:
            print(f"  parsed {len(page_listings)} listings", file=sys.stderr)

        # Save page 1 for diagnostics if parsing produced nothing.
        if i == 1 and not page_listings:
            Path("debug_page_1.html").write_text(html, encoding="utf-8")
            print(
                "  WROTE DIAGNOSTICS: debug_page_1.html",
                file=sys.stderr,
            )

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

        time.sleep(random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC))

    return list(results.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-acres", type=float, default=1.0)
    parser.add_argument("--max-price", type=float, default=25000.0)
    parser.add_argument("--out", type=Path, default=Path("florida_lots.json"))
    parser.add_argument(
        "--site",
        choices=sorted(SITES),
        default=DEFAULT_SITE,
        help=f"Which site to scrape (default: {DEFAULT_SITE})",
    )
    parser.add_argument(
        "--stealth",
        action="store_true",
        help="Force the stealth proxy (75 credits/page). "
        "Auto-enabled for landwatch.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    listings = scrape(
        args.min_acres,
        args.max_price,
        site=args.site,
        stealth=True if args.stealth else None,
        verbose=not args.quiet,
    )
    write_json(listings, args.out)
    print(f"\nSaved {len(listings)} listings to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
