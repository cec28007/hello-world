#!/usr/bin/env python3
"""
analyze_roster.py — cross-reference a SWGOH roster export against the curated
meta-teams database and report what to build toward.

Usage:
    python3 analyze_roster.py <roster_export.json> [--teams meta_teams.json]
                              [--mode gac-def] [--relic-floor 5]

Input: a swgoh.gg-style export (the JSON with a "units" list; each unit has
data.base_id, rarity, gear_level, relic_tier, level, name).

Output: teams grouped by readiness — READY / CLOSE / PROJECT / LOCKED — with the
specific missing or under-leveled units, sorted so the highest-value, closest
teams surface first. This answers "which direction to build based on what I own."

NOTE ON RELICS: the export's raw `relic_tier` field is offset from the in-game
displayed relic. This script compares raw values consistently (relative
comparisons are valid); it labels them "r<n> raw" to avoid implying a display
number. Tune --relic-floor to your bracket (5 = baseline, 7 = GAC standard).
"""
import argparse
import json
import os
import sys

TIER_RANK = {"S": 0, "A": 1, "B": 2, "C": 3}
STATUS_RANK = {"READY": 0, "CLOSE": 1, "PROJECT": 2, "LOCKED": 3}


def load_roster(path):
    with open(path) as f:
        data = json.load(f)
    units = {}
    for entry in data.get("units", []):
        u = entry.get("data", entry)
        bid = u.get("base_id")
        if bid:
            units[bid] = u
    profile = data.get("data", {})
    return units, profile


def unit_state(units, bid):
    u = units.get(bid)
    if not u:
        return None
    def num(v):
        return v if isinstance(v, int) else 0
    return {
        "base_id": bid,
        "name": u.get("name", bid),
        "rarity": num(u.get("rarity")),
        "gear": num(u.get("gear_level")),
        "relic": num(u.get("relic_tier")),
        "level": num(u.get("level")),
        "is_ship": num(u.get("combat_type")) == 2,
    }


def is_underleveled(st, relic_floor):
    # Ships have no relics — they scale off crew. Judge them by star level.
    if st["is_ship"]:
        return st["rarity"] < 7
    return st["relic"] < relic_floor


def analyze_team(units, team, relic_floor):
    """Return a readiness assessment for one team."""
    core = [team["leader"]] + team.get("members", [])
    alts = team.get("alternates", [])

    owned, missing, underleveled = [], [], []
    leader_owned = units.get(team["leader"]) is not None

    for bid in core:
        st = unit_state(units, bid)
        if st is None:
            missing.append(bid)
        else:
            owned.append(st)
            if is_underleveled(st, relic_floor):
                underleveled.append(st)

    # try to backfill missing core slots (not leader) with owned alternates
    filled_by_alt = []
    if missing:
        avail_alts = [unit_state(units, a) for a in alts]
        avail_alts = [a for a in avail_alts if a]
        for a in avail_alts:
            if len(filled_by_alt) < len([m for m in missing if m != team["leader"]]):
                filled_by_alt.append(a)

    missing_after_alts = max(0, len([m for m in missing if m != team["leader"]]) - len(filled_by_alt))
    leader_missing = team["leader"] in missing

    # readiness status
    if leader_missing:
        status = "LOCKED"
    elif missing_after_alts >= 2:
        status = "PROJECT"
    elif missing_after_alts == 1 or underleveled:
        status = "CLOSE"
    else:
        status = "READY"

    return {
        "name": team["name"],
        "faction": team.get("faction", ""),
        "tier": team.get("tier", "C"),
        "modes": team.get("modes", []),
        "notes": team.get("notes", ""),
        "status": status,
        "leader_owned": leader_owned,
        "owned": owned,
        "missing": missing,
        "underleveled": underleveled,
        "filled_by_alt": filled_by_alt,
    }


def fmt_unit(st):
    return "{} ({}* g{} r{})".format(st["name"], st["rarity"], st["gear"], st["relic"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roster")
    ap.add_argument("--teams", default=os.path.join(
        os.path.dirname(__file__), "..", "data", "meta_teams.json"))
    ap.add_argument("--mode", default=None,
                    help="filter to one mode, e.g. gac-def, gac-off, fleet, tw")
    ap.add_argument("--relic-floor", type=int, default=5,
                    help="raw relic_tier considered 'ready' (default 5)")
    args = ap.parse_args()

    units, profile = load_roster(args.roster)
    with open(args.teams) as f:
        db = json.load(f)

    name = profile.get("name", "?")
    ac = profile.get("ally_code", "?")
    print("=" * 70)
    print("ROSTER ANALYSIS — {} ({})   units: {}".format(name, ac, len(units)))
    if args.mode:
        print("Mode filter: {}".format(args.mode))
    print("Relic floor (raw): r{}".format(args.relic_floor))
    print("=" * 70)

    results = []
    for team in db["teams"]:
        if args.mode and args.mode not in team.get("modes", []):
            continue
        results.append(analyze_team(units, team, args.relic_floor))

    results.sort(key=lambda r: (STATUS_RANK[r["status"]], TIER_RANK.get(r["tier"], 9)))

    for r in results:
        print("\n[{}] {}  —  {} tier  {}".format(
            r["status"], r["name"], r["tier"], "/".join(r["modes"])))
        if r["missing"]:
            miss_names = [units.get(m, {}).get("name", m) if units.get(m) else m
                          for m in r["missing"]]
            print("   MISSING: {}".format(", ".join(miss_names)))
        if r["filled_by_alt"]:
            print("   (alt fills: {})".format(
                ", ".join(fmt_unit(a) for a in r["filled_by_alt"])))
        if r["underleveled"]:
            print("   UNDER r{}: {}".format(
                args.relic_floor, ", ".join(fmt_unit(u) for u in r["underleveled"])))
        if r["status"] == "READY":
            print("   -> deployable now")
        if r["notes"]:
            print("   note: {}".format(r["notes"]))

    print("\n" + "=" * 70)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("SUMMARY: " + "  ".join(
        "{}={}".format(k, counts.get(k, 0))
        for k in ["READY", "CLOSE", "PROJECT", "LOCKED"]))
    print("Build-toward priority = CLOSE teams at S/A tier (biggest payoff, "
          "least work).")


if __name__ == "__main__":
    main()
