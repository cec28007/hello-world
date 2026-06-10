#!/usr/bin/env python3
"""Pull a SWGOH player's current state by ally code from the public swgoh.gg API.

Usage:
    python3 swgoh_pull.py 611-121-817
    python3 swgoh_pull.py 611121817 --json roster.json

The swgoh.gg player API is public and needs no authentication. This script
prints a summary of the player's current state and can optionally dump the
full JSON response (profile + roster) to a file.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

API_URL = "https://swgoh.gg/api/player/{ally_code}/"


def normalize_ally_code(raw: str) -> str:
    """Strip dashes/spaces; expect 9 digits (e.g. 611-121-817 -> 611121817)."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) != 9:
        raise ValueError(
            f"Ally code must be 9 digits, got {len(digits)!r} from input {raw!r}"
        )
    return digits


def fetch_player(ally_code: str) -> dict:
    url = API_URL.format(ally_code=ally_code)
    req = urllib.request.Request(url, headers={"User-Agent": "swgoh-pull/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def summarize(payload: dict) -> str:
    data = payload.get("data", {})
    units = payload.get("units", [])

    characters = [u for u in units if u.get("data", {}).get("combat_type") == 1]
    ships = [u for u in units if u.get("data", {}).get("combat_type") == 2]

    lines = [
        f"Name:            {data.get('name', '?')}",
        f"Ally code:       {data.get('ally_code', '?')}",
        f"Level:           {data.get('level', '?')}",
        f"Guild:           {data.get('guild_name', '(none)')}",
        f"Galactic Power:  {data.get('galactic_power', '?'):,}"
        if isinstance(data.get("galactic_power"), int)
        else f"Galactic Power:  {data.get('galactic_power', '?')}",
        f"  Characters GP: {data.get('character_galactic_power', '?')}",
        f"  Ships GP:      {data.get('ship_galactic_power', '?')}",
        f"Characters:      {len(characters)} unlocked",
        f"Ships:           {len(ships)} unlocked",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Pull SWGOH player state by ally code.")
    parser.add_argument("ally_code", help="Ally code, e.g. 611-121-817 or 611121817")
    parser.add_argument(
        "--json",
        metavar="FILE",
        help="Write the full JSON response (profile + roster) to FILE",
    )
    args = parser.parse_args(argv)

    try:
        ally_code = normalize_ally_code(args.ally_code)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        payload = fetch_player(ally_code)
    except urllib.error.HTTPError as exc:
        print(f"Error: API returned HTTP {exc.code} for ally code {ally_code}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Error: could not reach swgoh.gg ({exc.reason})", file=sys.stderr)
        return 1

    print(summarize(payload))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\nFull JSON written to {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
