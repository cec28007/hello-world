#!/usr/bin/env python3
"""Guided entry tool for the Tesla ownership dashboard.

Reads and rewrites the JSON object inside data.js so you don't have to edit
it by hand. No third-party dependencies — just `python3 add_entry.py`.

Usage:
    python3 add_entry.py            # interactive menu
    python3 add_entry.py odometer   # jump straight to a category
"""
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "data.js")
PREFIX = "window.TESLA_DATA = "


def load():
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        text = fh.read()
    start = text.index("{", text.rindex(PREFIX))
    depth, end = 0, None
    for i in range(start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit("Could not parse data.js — is the object intact?")
    obj = json.loads(text[start:end])
    return text, start, end, obj


def save(text, start, end, obj):
    body = json.dumps(obj, indent=2, ensure_ascii=False)
    new_text = text[:start] + body + text[end:]
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    print("\n✓ Saved to data.js — refresh index.html to see it.")


def ask(label, cast=str, default=None, optional=False):
    suffix = f" [{default}]" if default is not None else (" (optional)" if optional else "")
    while True:
        raw = input(f"  {label}{suffix}: ").strip()
        if not raw:
            if default is not None:
                return default
            if optional:
                return ""
            print("    (required)")
            continue
        try:
            return cast(raw)
        except ValueError:
            print("    Invalid value, try again.")


def add_odometer(obj):
    print("\nNew odometer reading:")
    obj["odometer_readings"].append({
        "date": ask("Date (YYYY-MM-DD)", default=str(date.today())),
        "odometer": ask("Odometer (mi)", int),
        "note": ask("Note", optional=True),
    })


def add_battery(obj):
    print("\nNew battery test:")
    obj["battery_tests"].append({
        "date": ask("Date (YYYY-MM-DD)", default=str(date.today())),
        "odometer": ask("Odometer (mi)", int),
        "rated_range_100pct_mi": ask("Rated range at 100% (mi)", int),
        "method": ask("Method", default="Display @ 100%"),
        "note": ask("Note", optional=True),
    })


def add_service(obj):
    print("\nNew service record:")
    obj["service_history"].append({
        "date": ask("Date (YYYY-MM-DD)", default=str(date.today())),
        "odometer": ask("Odometer (mi)", int),
        "category": ask("Category (Maintenance/Repair/Tires/Upgrade)", default="Maintenance"),
        "description": ask("Description"),
        "cost": ask("Cost ($)", float, default=0),
        "vendor": ask("Vendor", optional=True),
    })


def add_resale(obj):
    print("\nNew resale estimate:")
    obj["resale_estimates"].append({
        "date": ask("Date (YYYY-MM-DD)", default=str(date.today())),
        "odometer": ask("Odometer (mi)", int),
        "value": ask("Estimated value ($)", int),
        "source": ask("Source (e.g. KBB private party)", optional=True),
    })


def add_wheel(obj):
    print("\nNew wheel/tire setup:")
    active = ask("Currently on the car? (y/n)", default="n").lower().startswith("y")
    if active:
        for w in obj["wheel_setups"]:
            w["active"] = False
    obj["wheel_setups"].append({
        "name": ask("Name (e.g. Summer, Track, Winter)"),
        "active": active,
        "season": ask("Season", optional=True),
        "wheel": ask("Wheel"),
        "tire_brand": ask("Tire brand"),
        "tire_size": ask("Tire size (e.g. 235/35R20)"),
        "installed_date": ask("Installed date (YYYY-MM-DD)", default=str(date.today())),
        "odometer_installed": ask("Odometer installed (mi)", int),
        "notes": ask("Notes", optional=True),
    })


ACTIONS = {
    "odometer": ("Odometer reading", add_odometer),
    "battery": ("Battery test", add_battery),
    "service": ("Service record", add_service),
    "resale": ("Resale estimate", add_resale),
    "wheel": ("Wheel/tire setup", add_wheel),
}


def main():
    text, start, end, obj = load()
    keys = list(ACTIONS)

    choice = sys.argv[1].lower() if len(sys.argv) > 1 else None
    if choice not in ACTIONS:
        print("What do you want to add?")
        for i, k in enumerate(keys, 1):
            print(f"  {i}. {ACTIONS[k][0]}")
        sel = input("Choose 1-%d: " % len(keys)).strip()
        try:
            choice = keys[int(sel) - 1]
        except (ValueError, IndexError):
            raise SystemExit("Nothing added.")

    ACTIONS[choice][1](obj)
    save(text, start, end, obj)


if __name__ == "__main__":
    main()
