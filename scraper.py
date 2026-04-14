"""
Florida vacant-land scraper (LandWatch).

Searches LandWatch for Florida lots that are:
  - for sale
  - larger than MIN_ACRES (default 1 acre)
  - priced under MAX_PRICE (default $25,000)

Writes results to a JSON file.

IMPORTANT
---------
LandWatch's Terms of Service prohibit automated scraping. This script is
provided for personal research only. Run it slowly, do not redistribute the
scraped data, and stop if the site asks you to.

If LandWatch responds with HTTP 403 or a CAPTCHA page, the plain-requests
approach will not work -- you will need a headless browser (Playwright) to
pass their bot check. This script will detect the block and tell you.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Site adapters
# ---------------------------------------------------------------------------
#
# Each adapter is a dict with:
#   base_url          canonical origin
#   page_url(mn, mx, page) -> str      builds the results URL for a page number
#
# The HTML parser (``parse_listings``) is site-agnostic because it walks
# schema.org JSON-LD, which every major real-estate site embeds.


def _landsearch_url(min_acres: float, max_price: float, page: int) -> str:
    base = (
        f"https://www.landsearch.com/properties/florida/search/"
        f"under-{int(max_price)}/{int(min_acres)}-acres"
    )
    return base if page == 1 else f"{base}/page/{page}"


def _landflip_url(min_acres: float, max_price: float, page: int) -> str:
    base = (
        f"https://www.landflip.com/land-for-sale/florida/"
        f"1-minprice/{int(max_price)}-maxprice/{int(min_acres)}-minacreage"
    )
    return base if page == 1 else f"{base}/page/{page}"


def _landwatch_url(min_acres: float, max_price: float, page: int) -> str:
    base = (
        f"https://www.landwatch.com/florida-land-for-sale/available/"
        f"under-{int(max_price)}/acres-over-{int(min_acres)}"
    )
    return base if page == 1 else f"{base}/page-{page}"


def _landandfarm_url(min_acres: float, max_price: float, page: int) -> str:
    base = (
        f"https://www.landandfarm.com/search/florida-land-for-sale/"
        f"?price-max={int(max_price)}&acres-min={int(min_acres)}"
    )
    return base if page == 1 else f"{base}&page={page}"


SITES: dict[str, dict] = {
    "landsearch": {"base_url": "https://www.landsearch.com", "page_url": _landsearch_url},
    "landflip": {"base_url": "https://www.landflip.com", "page_url": _landflip_url},
    "landwatch": {"base_url": "https://www.landwatch.com", "page_url": _landwatch_url},
    "landandfarm": {"base_url": "https://www.landandfarm.com", "page_url": _landandfarm_url},
}

DEFAULT_SITE = "landsearch"

# Back-compat alias used elsewhere in this module.
BASE_URL = SITES[DEFAULT_SITE]["base_url"]

# Rotate through a couple of realistic desktop User-Agents. LandWatch
# fingerprints aggressively on UA + Accept-Language + Accept combinations.
USER_AGENTS = [
    # Chrome 124 on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
    # Firefox 125 on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",
]

DEFAULT_HEADERS = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
}

# Be polite: random pause between page fetches.
MIN_DELAY_SEC = 3.0
MAX_DELAY_SEC = 7.0

# Safety cap so a bad URL pattern can't run forever.
MAX_PAGES = 200


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Listing:
    url: str
    title: str | None = None
    price: float | None = None
    acres: float | None = None
    address: str | None = None
    city: str | None = None
    county: str | None = None
    state: str | None = None
    description: str | None = None
    image: str | None = None


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    s.headers["User-Agent"] = random.choice(USER_AGENTS)
    return s


class BlockedError(RuntimeError):
    """Raised when LandWatch returns a bot-protection response."""


def fetch(session: requests.Session, url: str) -> str:
    resp = session.get(url, timeout=30, allow_redirects=True)
    if resp.status_code == 403 or resp.status_code == 429:
        raise BlockedError(
            f"LandWatch returned HTTP {resp.status_code} for {url}. "
            "Anti-bot protection is active -- switch to Playwright."
        )
    resp.raise_for_status()
    body = resp.text
    # LandWatch sometimes returns 200 with a Cloudflare/PerimeterX interstitial.
    lowered = body.lower()
    if (
        "captcha" in lowered
        and "id=\"captcha" in lowered
        or "access denied" in lowered
        or "verify you are human" in lowered
    ):
        raise BlockedError(
            f"Received a bot-check interstitial page for {url}. "
            "Switch to Playwright or try again later."
        )
    return body


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

ACRES_RE = re.compile(r"([\d,.]+)\s*ac", re.IGNORECASE)
PRICE_RE = re.compile(r"\$\s*([\d,]+)")


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").replace("$", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _iter_jsonld_objects(soup: BeautifulSoup) -> Iterator[dict]:
    """Yield every JSON object found in <script type=application/ld+json> tags."""
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    yield item
        elif isinstance(data, dict):
            yield data
            # Pages often wrap listings inside an ItemList -> itemListElement.
            for key in ("itemListElement", "@graph"):
                value = data.get(key)
                if isinstance(value, list):
                    for entry in value:
                        if isinstance(entry, dict):
                            inner = entry.get("item") if "item" in entry else entry
                            if isinstance(inner, dict):
                                yield inner


def _listing_from_jsonld(obj: dict) -> Listing | None:
    """Convert a schema.org Product / RealEstateListing dict to a Listing."""
    obj_type = obj.get("@type")
    if isinstance(obj_type, list):
        types = {t.lower() for t in obj_type if isinstance(t, str)}
    elif isinstance(obj_type, str):
        types = {obj_type.lower()}
    else:
        types = set()

    wanted = {"product", "realestatelisting", "singlefamilyresidence", "house",
              "apartment", "place", "residence", "offer"}
    if not types & wanted:
        return None

    url = obj.get("url") or obj.get("@id")
    if not url:
        return None

    # Price can live under offers.price or directly on the object.
    price = None
    offers = obj.get("offers")
    if isinstance(offers, dict):
        price = _to_float(offers.get("price"))
    elif isinstance(offers, list) and offers:
        price = _to_float(offers[0].get("price") if isinstance(offers[0], dict) else None)
    if price is None:
        price = _to_float(obj.get("price"))

    # Address: could be string or PostalAddress object.
    address = obj.get("address")
    city = region = street = None
    if isinstance(address, dict):
        street = address.get("streetAddress")
        city = address.get("addressLocality")
        region = address.get("addressRegion")
        address_str = ", ".join(
            p for p in (street, city, region, address.get("postalCode")) if p
        )
    elif isinstance(address, str):
        address_str = address
    else:
        address_str = None

    # Acreage usually shows up in name/description; look for "X acres".
    acres = None
    for field in (obj.get("name"), obj.get("description")):
        if isinstance(field, str):
            m = ACRES_RE.search(field)
            if m:
                acres = _to_float(m.group(1))
                if acres is not None:
                    break

    image = obj.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url")

    return Listing(
        url=urljoin(BASE_URL, url),
        title=obj.get("name"),
        price=price,
        acres=acres,
        address=address_str,
        city=city,
        state=region,
        description=obj.get("description") if isinstance(obj.get("description"), str) else None,
        image=image if isinstance(image, str) else None,
    )


def _listing_from_card(card) -> Listing | None:
    """CSS-selector fallback when JSON-LD is missing or incomplete."""
    anchor = card.find("a", href=True)
    if not anchor:
        return None
    url = urljoin(BASE_URL, anchor["href"])

    text = card.get_text(" ", strip=True)
    price = None
    m = PRICE_RE.search(text)
    if m:
        price = _to_float(m.group(1))

    acres = None
    m = ACRES_RE.search(text)
    if m:
        acres = _to_float(m.group(1))

    title = anchor.get("title") or (anchor.get_text(strip=True) or None)
    return Listing(url=url, title=title, price=price, acres=acres)


def parse_listings(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")

    found: dict[str, Listing] = {}

    # Primary: JSON-LD.
    for obj in _iter_jsonld_objects(soup):
        listing = _listing_from_jsonld(obj)
        if listing and listing.url not in found:
            found[listing.url] = listing

    # Fallback: look for listing cards. LandWatch has historically used
    # elements like <div data-testid="property-card"> or class names
    # containing "result" / "listing". Try a couple of selectors.
    if not found:
        candidates = soup.select(
            '[data-testid*="property"], [data-testid*="listing"], '
            'article, li[class*="result"], div[class*="listing"]'
        )
        for card in candidates:
            listing = _listing_from_card(card)
            if listing and listing.url not in found and "/property/" in listing.url:
                found[listing.url] = listing

    return list(found.values())


def detect_last_page(html: str) -> int | None:
    """Return the highest page number linked from pagination, if any."""
    soup = BeautifulSoup(html, "html.parser")
    highest = None
    for a in soup.find_all("a", href=True):
        m = re.search(r"/page-(\d+)\b", a["href"])
        if m:
            n = int(m.group(1))
            if highest is None or n > highest:
                highest = n
    return highest


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def passes_filters(
    listing: Listing, min_acres: float, max_price: float
) -> bool:
    # Treat unknown values conservatively: require the server-side filter to
    # have already restricted the page, so unknown price / acres still gets
    # kept (better to over-collect than silently drop).
    if listing.price is not None and listing.price >= max_price:
        return False
    if listing.acres is not None and listing.acres < min_acres:
        return False
    return True


# ---------------------------------------------------------------------------
# Scrape loop
# ---------------------------------------------------------------------------


def page_urls(
    min_acres: float, max_price: float, site: str = DEFAULT_SITE
) -> Iterator[str]:
    if site not in SITES:
        raise ValueError(f"Unknown site {site!r}; choose from {list(SITES)}")
    build = SITES[site]["page_url"]
    for page in range(1, MAX_PAGES + 1):
        yield build(min_acres, max_price, page)


def scrape(
    min_acres: float,
    max_price: float,
    *,
    site: str = DEFAULT_SITE,
    verbose: bool = True,
) -> list[Listing]:
    session = build_session()
    results: dict[str, Listing] = {}
    last_page: int | None = None

    for i, url in enumerate(page_urls(min_acres, max_price, site), start=1):
        if last_page is not None and i > last_page:
            break
        if verbose:
            print(f"[page {i}] GET {url}", file=sys.stderr)

        try:
            html = fetch(session, url)
        except BlockedError as exc:
            print(f"\nBLOCKED: {exc}", file=sys.stderr)
            break
        except requests.RequestException as exc:
            print(f"  request failed: {exc}", file=sys.stderr)
            break

        page_listings = parse_listings(html)
        if verbose:
            print(f"  parsed {len(page_listings)} listings", file=sys.stderr)

        if not page_listings:
            # Either we're past the last page or the parser is broken.
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
            # Nothing new -- likely pagination rolled past the end.
            break

        if last_page is None:
            last_page = detect_last_page(html)
            if verbose and last_page:
                print(f"  detected last page = {last_page}", file=sys.stderr)

        time.sleep(random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC))

    return list(results.values())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def write_json(listings: Iterable[Listing], path: Path) -> None:
    data = [asdict(l) for l in listings]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-acres", type=float, default=1.0)
    parser.add_argument("--max-price", type=float, default=25000.0)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("florida_lots.json"),
        help="Output JSON file (default: florida_lots.json)",
    )
    parser.add_argument(
        "--site",
        choices=sorted(SITES),
        default=DEFAULT_SITE,
        help=f"Which site to scrape (default: {DEFAULT_SITE})",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    listings = scrape(
        args.min_acres,
        args.max_price,
        site=args.site,
        verbose=not args.quiet,
    )

    write_json(listings, args.out)
    print(
        f"\nSaved {len(listings)} listings to {args.out}", file=sys.stderr
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
