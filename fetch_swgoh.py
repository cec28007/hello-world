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

Guild data is available too:

    --guild           also pull the player's guild (id taken from their profile)
    --guild-id <id>   pull a specific guild by its swgoh.gg id (no ally needed)

No outbound access to swgoh.gg? Render from JSON you saved/pasted instead
(open https://swgoh.gg/api/player/<ally_code>/ in a browser and save it):

    --from-file <path>        render a saved player JSON ('-' reads stdin)
    --guild-from-file <path>  render a saved guild JSON

Config is read from environment variables, or from a local `swgoh_config.json`
(git-ignored) of the same keys:

    SWGOH_ALLY_CODE   ally code, with or without dashes (e.g. 611-121-817)
    SWGOH_GUILD_ID    guild id (used by --guild if no profile is fetched)
    SWGOH_BACKEND     live | mock
    SWGOH_OUT         output path for the player JSON (default swgoh_data.json)
    SWGOH_GUILD_OUT   output path for the guild JSON (default swgoh_guild_data.json)

Examples:

    python3 fetch_swgoh.py --ally 611-121-817
    SWGOH_ALLY_CODE=611121817 python3 fetch_swgoh.py
    python3 fetch_swgoh.py mock --dry-run
    python3 fetch_swgoh.py --ally 611121817 --units 15
    python3 fetch_swgoh.py --ally 611-121-817 --guild        # player + guild
    python3 fetch_swgoh.py --guild-id 1a2b3c4d-... --units 20  # guild only

The player response is saved to swgoh_data.json and the guild response to
swgoh_guild_data.json (both git-ignored); summaries are printed to the terminal.
"""
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "swgoh_config.json")
DEFAULT_OUT = os.path.join(HERE, "swgoh_data.json")
DEFAULT_GUILD_OUT = os.path.join(HERE, "swgoh_guild_data.json")

API = "https://swgoh.gg/api/player/%s/"
GUILD_API = "https://swgoh.gg/api/guild-profile/%s/"
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


def _load_json(path):
    """Load a saved swgoh.gg JSON response; '-' reads stdin."""
    try:
        if path == "-":
            return json.load(sys.stdin)
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise SystemExit("No such file: %s" % path)
    except json.JSONDecodeError as e:
        raise SystemExit("%s is not valid JSON: %s" % (path, e))


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


# ---- backends: each returns parsed swgoh.gg JSON --------------------------

def _get_json(url, not_found_msg):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise SystemExit(not_found_msg)
        if e.code == 403:
            raise SystemExit(
                "swgoh.gg returned 403 Forbidden. This usually means outbound "
                "access to swgoh.gg is blocked (network policy) or the request "
                "was bot-filtered. Try again from an unrestricted network.")
        raise SystemExit("swgoh.gg request failed: HTTP %s %s" % (e.code, e.reason))
    except urllib.error.URLError as e:
        raise SystemExit("Could not reach swgoh.gg: %s" % e.reason)


def fetch_player_live(ally):
    return _get_json(
        API % ally,
        "swgoh.gg has no profile for ally code %s. Make sure the code is correct "
        "and the profile is public/synced on swgoh.gg." % ally)


def fetch_guild_live(guild_id):
    return _get_json(
        GUILD_API % guild_id,
        "swgoh.gg has no guild with id %s. The id comes from a player's profile; "
        "make sure the guild is public/synced on swgoh.gg." % guild_id)


def fetch_player_mock(ally):
    return {
        "data": {
            "name": "Mock Commander",
            "ally_code": int(ally),
            "level": 85,
            "guild_name": "Mock Guild",
            "guild_id": "mock-guild-0001",
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


def fetch_guild_mock(guild_id):
    return {
        "data": {
            "name": "Mock Guild",
            "guild_id": guild_id,
            "member_count": 3,
            "galactic_power": 12345678,
            "external_message": "May the Force be with you (mock).",
            "members": [
                {"player_name": "Mock Commander", "galactic_power": 5123456, "player_level": 85},
                {"player_name": "Mock Lieutenant", "galactic_power": 4500000, "player_level": 85},
                {"player_name": "Mock Recruit", "galactic_power": 2721222, "player_level": 84},
            ],
        },
    }


PLAYER_BACKENDS = {"live": fetch_player_live, "mock": fetch_player_mock}
GUILD_BACKENDS = {"live": fetch_guild_live, "mock": fetch_guild_mock}


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


def _member_fields(m):
    """Normalize a guild member entry to (name, gp), tolerating shapes."""
    if isinstance(m, dict) and "data" in m and isinstance(m["data"], dict):
        m = m["data"]  # some endpoints nest the player under "data"
    name = m.get("player_name") or m.get("name") or "?"
    gp = m.get("galactic_power") or m.get("player_galactic_power") or 0
    return name, gp


def print_guild_summary(payload, top_n):
    data = payload.get("data") or payload.get("guild") or {}
    members = (data.get("members") or payload.get("members")
               or payload.get("players") or [])

    print("=" * 60)
    print("Guild:         %s" % data.get("name", "n/a"))
    print("Guild id:      %s" % data.get("guild_id", "n/a"))
    member_count = data.get("member_count") or len(members)
    print("Members:       %s" % (member_count or "n/a"))
    print("Galactic Power: %s" % fmt_int(data.get("galactic_power")))
    msg = data.get("external_message")
    if msg:
        print("Message:       %s" % msg)
    print("-" * 60)

    if top_n and members:
        ranked = sorted(members, key=lambda m: _member_fields(m)[1] or 0, reverse=True)
        print("Top %d members by galactic power:" % min(top_n, len(ranked)))
        for m in ranked[:top_n]:
            name, gp = _member_fields(m)
            print("  %-28s %s GP" % (str(name)[:28], fmt_int(gp)))
    print("=" * 60)


def main():
    # Hand-rolled parser so option values (--ally 611-121-817) aren't mistaken
    # for positional backend names.
    dry = False
    ally_arg = None
    guild_flag = False
    guild_id_arg = None
    from_file = None
    guild_from_file = None
    top_n = 10
    positionals = []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--dry-run", "-n"):
            dry = True
        elif a == "--guild":
            guild_flag = True
        elif a.startswith("--guild-from-file"):
            guild_from_file, i = _opt_value(a, argv, i)
            guild_flag = True
        elif a.startswith("--guild-id"):
            guild_id_arg, i = _opt_value(a, argv, i)
            guild_flag = True
        elif a.startswith("--from-file"):
            from_file, i = _opt_value(a, argv, i)
        elif a.startswith("--ally"):
            ally_arg, i = _opt_value(a, argv, i)
        elif a.startswith("--units"):
            val, i = _opt_value(a, argv, i)
            top_n = int(val)
        elif not a.startswith("-"):
            positionals.append(a)
        i += 1

    # Offline mode: render summaries from JSON saved/pasted from swgoh.gg
    # (open https://swgoh.gg/api/player/<code>/ in a browser, save the JSON).
    # No network, so it works even where swgoh.gg egress is blocked.
    if from_file or guild_from_file:
        if from_file:
            payload = _load_json(from_file)
            print_summary(payload, top_n)
        if guild_from_file:
            if from_file:
                print()
            print_guild_summary(_load_json(guild_from_file), top_n)
        return

    backend = (positionals[0] if positionals and not positionals[0].isdigit()
               else cfg("SWGOH_BACKEND", "live")).lower()
    if backend not in PLAYER_BACKENDS:
        raise SystemExit("Unknown backend %r. Choose: %s"
                         % (backend, ", ".join(PLAYER_BACKENDS)))

    raw_ally = (ally_arg or cfg("SWGOH_ALLY_CODE")
                or (positionals[0] if positionals and positionals[0].isdigit() else None))
    guild_id = guild_id_arg or cfg("SWGOH_GUILD_ID")
    # Guild-only run: a guild id was given and there's no ally code to fetch.
    guild_only = guild_flag and guild_id and not raw_ally

    if not raw_ally and backend == "mock" and not guild_only:
        raw_ally = "123456789"  # mock needs no real code
    if not raw_ally and not guild_only:
        raise SystemExit("No ally code. Pass --ally 611-121-817 or set "
                         "SWGOH_ALLY_CODE (or use --guild-id for a guild-only pull).")

    out = cfg("SWGOH_OUT", DEFAULT_OUT)
    guild_out = cfg("SWGOH_GUILD_OUT", DEFAULT_GUILD_OUT)
    writes = []  # (path, payload) pairs to flush unless --dry-run

    if not guild_only:
        ally = normalize_ally(raw_ally)
        print("Fetching ally code %s via %s backend...\n" % (ally, backend))
        payload = PLAYER_BACKENDS[backend](ally)
        print_summary(payload, top_n)
        writes.append((out, payload))
        # Pull the guild id off the profile if --guild was given without one.
        if guild_flag and not guild_id:
            guild_id = (payload.get("data") or {}).get("guild_id")
            if not guild_id:
                print("\n! --guild requested but this profile has no guild id "
                      "(not in a guild, or field missing). Skipping guild fetch.")

    if guild_flag and guild_id:
        print("\nFetching guild %s via %s backend...\n" % (guild_id, backend))
        guild_payload = GUILD_BACKENDS[backend](guild_id)
        print_guild_summary(guild_payload, top_n)
        writes.append((guild_out, guild_payload))

    if dry:
        print("\n[dry run] No files written.")
        return
    for path, data in writes:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print("\n✓ Saved %s" % os.path.relpath(path, HERE))


if __name__ == "__main__":
    main()
