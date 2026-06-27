#!/usr/bin/env python3
"""Pull a player's Star Wars: Galaxy of Heroes profile from swgoh.gg.

swgoh.gg exposes a free, read-only JSON API keyed on ally code. No token is
needed, but the player's profile must be public/synced on swgoh.gg for data
to come back.

Backends (set SWGOH_BACKEND or pass as the first positional argument):

  live   Default. Fetches https://swgoh.gg/api/player/<ally_code>/ over the
         network. Needs outbound access to swgoh.gg.

  mock   No network. Returns a tiny canned profile so you can test the
         pipeline / output formatting offline.

Config is read from environment variables, or from a local `swgoh_config.json`
(git-ignored) of the same keys:

    SWGOH_ALLY_CODE   ally code, with or without dashes (e.g. 611-121-817)
    SWGOH_BACKEND     live | mock
    SWGOH_OUT         output path for the raw JSON (default swgoh_data.json)

Examples:

    python3 fetch_swgoh.py --ally 611-121-817
    SWGOH_ALLY_CODE=611121817 python3 fetch_swgoh.py
    python3 fetch_swgoh.py mock --dry-run
    python3 fetch_swgoh.py --ally 611121817 --units 15

The full API response is saved to swgoh_data.json (git-ignored); a summary and
the top roster units by power are printed to the terminal.
"""
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "swgoh_config.json")
DEFAULT_OUT = os.path.join(HERE, "swgoh_data.json")

API = "https://swgoh.gg/api/player/%s/"
# swgoh.gg sits behind a bot filter that rejects the default urllib UA.
USER_AGENT = "Mozilla/5.0 (compatible; swgoh-fetch/1.0; +https://swgoh.gg)"


def cfg(key, default=None):
    if key in os.environ:
        return os.environ[key]
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        if key in data:
            return data[key]
    return default


def _opt_value(arg, argv, i):
    """Value for --opt=VALUE or --opt VALUE; returns (value, new_index)."""
    if "=" in arg:
        return arg.split("=", 1)[1], i
    if i + 1 < len(argv):
        return argv[i + 1], i + 1
    raise SystemExit("Option %s needs a value." % arg)


def normalize_ally(code):
    """Strip dashes/spaces; SWGOH ally codes are 9 digits."""
    digits = "".join(ch for ch in str(code) if ch.isdigit())
    if len(digits) != 9:
        raise SystemExit("Ally code %r should be 9 digits (got %d)." % (code, len(digits)))
    return digits


# ---- backends: each returns the parsed swgoh.gg player JSON ----------------

def fetch_live(ally):
    url = API % ally
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise SystemExit(
                "swgoh.gg has no profile for ally code %s. Make sure the code is "
                "correct and the profile is public/synced on swgoh.gg." % ally)
        if e.code == 403:
            raise SystemExit(
                "swgoh.gg returned 403 Forbidden. This usually means outbound "
                "access to swgoh.gg is blocked (network policy) or the request "
                "was bot-filtered. Try again from an unrestricted network.")
        raise SystemExit("swgoh.gg request failed: HTTP %s %s" % (e.code, e.reason))
    except urllib.error.URLError as e:
        raise SystemExit("Could not reach swgoh.gg: %s" % e.reason)


def fetch_mock(ally):
    return {
        "data": {
            "name": "Mock Commander",
            "ally_code": int(ally),
            "level": 85,
            "guild_name": "Mock Guild",
            "galactic_power": 5123456,
            "character_galactic_power": 3100000,
            "ship_galactic_power": 2023456,
            "arena_rank": 42,
            "fleet_arena": {"rank": 17},
        },
        "units": [
            {"data": {"base_id": "GLREY", "name": "Rey (Mock)", "combat_type": 1,
                      "rarity": 7, "level": 85, "gear_level": 13, "relic_tier": 9,
                      "power": 41234}},
            {"data": {"base_id": "JABBA", "name": "Jabba (Mock)", "combat_type": 1,
                      "rarity": 7, "level": 85, "gear_level": 13, "relic_tier": 7,
                      "power": 38120}},
        ],
    }


BACKENDS = {"live": fetch_live, "mock": fetch_mock}


def fmt_int(n):
    try:
        return "{:,}".format(int(n))
    except (TypeError, ValueError):
        return "n/a"


def unit_tier(u):
    """Human-readable gear/relic tier, e.g. 'R7' or 'G12'."""
    relic = u.get("relic_tier")
    # swgoh.gg encodes relic_tier as 1 (locked) then +1 per relic; 3 == Relic 1.
    if isinstance(relic, int) and relic >= 3:
        return "R%d" % (relic - 2)
    gear = u.get("gear_level")
    return "G%s" % gear if gear else "?"


def print_summary(payload, top_n):
    data = payload.get("data") or {}
    units = [u.get("data") or {} for u in payload.get("units") or []]

    print("=" * 60)
    print("Player:        %s" % data.get("name", "n/a"))
    print("Ally code:     %s" % data.get("ally_code", "n/a"))
    print("Level:         %s" % data.get("level", "n/a"))
    print("Guild:         %s" % data.get("guild_name", "n/a"))
    print("-" * 60)
    print("Galactic Power:       %s" % fmt_int(data.get("galactic_power")))
    print("  Characters:         %s" % fmt_int(data.get("character_galactic_power")))
    print("  Ships:              %s" % fmt_int(data.get("ship_galactic_power")))
    chars = [u for u in units if u.get("combat_type") == 1]
    ships = [u for u in units if u.get("combat_type") == 2]
    print("Roster:        %d units  (%d characters, %d ships)"
          % (len(units), len(chars), len(ships)))
    arena = data.get("arena_rank")
    fleet = (data.get("fleet_arena") or {}).get("rank")
    if arena or fleet:
        print("Arena rank:    squad %s / fleet %s" % (arena or "n/a", fleet or "n/a"))
    print("-" * 60)

    if top_n and chars:
        ranked = sorted(chars, key=lambda u: u.get("power") or 0, reverse=True)
        print("Top %d characters by power:" % min(top_n, len(ranked)))
        for u in ranked[:top_n]:
            print("  %-28s %-4s  %s GP"
                  % (u.get("name", "?")[:28], unit_tier(u), fmt_int(u.get("power"))))
    print("=" * 60)


def main():
    # Hand-rolled parser so option values (--ally 611-121-817) aren't mistaken
    # for positional backend names.
    dry = False
    ally_arg = None
    top_n = 10
    positionals = []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--dry-run", "-n"):
            dry = True
        elif a.startswith("--ally"):
            ally_arg, i = _opt_value(a, argv, i)
        elif a.startswith("--units"):
            val, i = _opt_value(a, argv, i)
            top_n = int(val)
        elif not a.startswith("-"):
            positionals.append(a)
        i += 1

    backend = (positionals[0] if positionals and not positionals[0].isdigit()
               else cfg("SWGOH_BACKEND", "live")).lower()
    if backend not in BACKENDS:
        raise SystemExit("Unknown backend %r. Choose: %s" % (backend, ", ".join(BACKENDS)))

    raw_ally = (ally_arg or cfg("SWGOH_ALLY_CODE")
                or (positionals[0] if positionals and positionals[0].isdigit() else None))
    if not raw_ally and backend == "mock":
        raw_ally = "123456789"  # mock needs no real code
    if not raw_ally:
        raise SystemExit("No ally code. Pass --ally 611-121-817 or set SWGOH_ALLY_CODE.")
    ally = normalize_ally(raw_ally)

    print("Fetching ally code %s via %s backend...\n" % (ally, backend))
    payload = BACKENDS[backend](ally)
    print_summary(payload, top_n)

    out = cfg("SWGOH_OUT", DEFAULT_OUT)
    if dry:
        print("\n[dry run] No file written.")
        return
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print("\n✓ Full response saved to %s" % os.path.relpath(out, HERE))


if __name__ == "__main__":
    main()
