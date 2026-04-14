#!/bin/bash
# Double-click this file to run the scraper via ScrapingBee.
# First run: asks for your ScrapingBee API key and saves it to .env.
# Subsequent runs: reads the key from .env and just runs.

set -e
cd "$(dirname "$0")"

echo "========================================"
echo "  Florida vacant-land scraper"
echo "  (via ScrapingBee)"
echo "========================================"
echo

if [ ! -f "scraper_scrapingbee.py" ]; then
    echo "ERROR: scraper_scrapingbee.py not found in $(pwd)."
    read -n 1 -r -s -p "Press any key to close..."
    exit 1
fi

# Pull latest changes on the feature branch.
echo "==> Updating from GitHub..."
git fetch origin claude/florida-lots-scraper-3Q570 >/dev/null 2>&1 || true
git checkout claude/florida-lots-scraper-3Q570 >/dev/null 2>&1 || true
git pull origin claude/florida-lots-scraper-3Q570 >/dev/null 2>&1 || true

# Virtualenv setup.
if [ ! -d ".venv" ]; then
    echo "==> Creating Python virtual environment (one-time)..."
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing Python packages..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Prompt for API key if we don't have one yet.
if [ ! -f ".env" ] || ! grep -q "^SCRAPINGBEE_API_KEY=" .env; then
    echo
    echo "==> ScrapingBee API key setup"
    echo "    1. Sign up (free, no credit card) at: https://www.scrapingbee.com"
    echo "    2. Copy your API key from the dashboard"
    echo
    read -r -p "Paste your ScrapingBee API key: " SB_KEY
    if [ -z "$SB_KEY" ]; then
        echo "No key entered; aborting."
        read -n 1 -r -s -p "Press any key to close..."
        exit 1
    fi
    # Preserve any other .env contents; replace/append SCRAPINGBEE_API_KEY.
    touch .env
    grep -v "^SCRAPINGBEE_API_KEY=" .env > .env.tmp || true
    echo "SCRAPINGBEE_API_KEY=$SB_KEY" >> .env.tmp
    mv .env.tmp .env
    chmod 600 .env
    echo "==> Saved API key to .env (gitignored)."
fi

# Try each site in order; stop at the first one that returns listings.
OUT="$(pwd)/florida_lots.json"
COUNT=0

# landsearch first (cheapest at ~10 credits/page, usually works).
# Then landflip, landandfarm, and finally landwatch (75 credits/page stealth).
for SITE in landsearch landflip landandfarm landwatch; do
    echo
    echo "==> Trying site: $SITE"
    echo
    python scraper_scrapingbee.py --site "$SITE" || true

    if [ -f "$OUT" ]; then
        COUNT=$(python -c "import json; print(len(json.load(open('$OUT'))))" 2>/dev/null || echo 0)
    fi

    if [ "$COUNT" -gt 0 ] 2>/dev/null; then
        echo
        echo "==> Got $COUNT listings from $SITE."
        break
    fi

    echo "==> $SITE returned 0 listings. Trying next site..."
done

echo
if [ "$COUNT" -gt 0 ] 2>/dev/null; then
    echo "==> Done. $COUNT listings saved to:"
    echo "    $OUT"
    open -R "$OUT" || true
else
    echo "==> All sites returned 0 listings."
    echo "    See debug_page_1.html for what the last site returned."
fi

echo
read -n 1 -r -s -p "Press any key to close this window..."
echo
