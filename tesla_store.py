#!/usr/bin/env python3
"""Shared read/write helpers for the dashboard's data.js store.

data.js holds plain JSON inside `window.TESLA_DATA = { ... }`. These helpers
parse that object, let callers mutate it, and write it back while preserving
the surrounding JS (the comment header and the assignment wrapper).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "data.js")
PREFIX = "window.TESLA_DATA = "


def load():
    """Return (text, start, end, obj) where obj is the parsed data object and
    text[start:end] is the JSON span inside data.js."""
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
    return text, start, end, json.loads(text[start:end])


def save(text, start, end, obj):
    """Write obj back into data.js, keeping the comment header and wrapper."""
    body = json.dumps(obj, indent=2, ensure_ascii=False)
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        fh.write(text[:start] + body + text[end:])


def upsert_by_date(items, entry, key="date"):
    """Insert entry, or replace an existing one with the same date.

    Returns "added" or "updated". Keeps a single row per date so re-running a
    fetch on the same day doesn't pile up duplicates.
    """
    for i, existing in enumerate(items):
        if existing.get(key) == entry.get(key):
            items[i] = entry
            return "updated"
    items.append(entry)
    return "added"
