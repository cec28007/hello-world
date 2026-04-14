#!/bin/bash
# Double-click this file in Finder to run the Florida lots scraper.
# First run: takes a few minutes (downloads Chromium ~150MB).
# Subsequent runs: just scrapes and opens the JSON.

set -e

# Run from this script's own directory (the cloned repo).
cd "$(dirname "$0")"

echo "========================================"
echo "  Florida vacant-land scraper"
echo "========================================"
echo

# Sanity check: are we inside the cloned repo?
if [ ! -f "scraper_playwright.py" ]; then
    echo "ERROR: scraper_playwright.py not found in $(pwd)."
    echo "Make sure this .command file is inside the cloned hello-world folder."
    echo
    read -n 1 -r -s -p "Press any key to close..."
    exit 1
fi

# Pull latest changes on the feature branch.
echo "==> Updating from GitHub..."
git fetch origin claude/florida-lots-scraper-3Q570 >/dev/null 2>&1 || true
git checkout claude/florida-lots-scraper-3Q570 >/dev/null 2>&1 || true
git pull origin claude/florida-lots-scraper-3Q570 >/dev/null 2>&1 || true

# Create a local virtualenv so we don't pollute the system Python.
if [ ! -d ".venv" ]; then
    echo "==> Creating Python virtual environment (one-time)..."
    python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# Install / update dependencies.
echo "==> Installing Python packages..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements-playwright.txt

# Install Chromium for Playwright (idempotent; fast after the first time).
echo "==> Ensuring Chromium is installed..."
python -m playwright install chromium

# Run the scraper. Try each supported site in order; stop at the first
# one that returns listings. This handles the case where one site's
# bot-protection blocks us but another doesn't.
OUT="$(pwd)/florida_lots.json"
COUNT=0

for SITE in landsearch landflip landandfarm landwatch; do
    echo
    echo "==> Trying site: $SITE (this can take a few minutes)"
    echo
    python scraper_playwright.py --site "$SITE" || true

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
    echo "    Check debug_page_1.html / debug_page_1.png for the last-tried site."
fi

echo
read -n 1 -r -s -p "Press any key to close this window..."
echo
