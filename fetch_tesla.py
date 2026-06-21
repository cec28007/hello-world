#!/usr/bin/env python3
"""Pull the car's current odometer + battery and append them to data.js.

Backends (set TESLA_BACKEND or pass as the first argument):

  tessie   Easiest. Needs a Tessie account (https://tessie.com). Config:
             TESSIE_TOKEN   API token from https://my.tessie.com/settings/api
             TESLA_VIN      your VIN (defaults to vehicle.vin in data.js)

  fleet    Official Tesla Fleet API (experimental — needs a registered
           developer app + paired virtual key). Config:
             TESLA_FLEET_BASE     regional base, e.g.
                                  https://fleet-api.prd.na.vn.cloud.tesla.com
             TESLA_CLIENT_ID      your app's client id
             TESLA_REFRESH_TOKEN  OAuth refresh token
             TESLA_VIN            your VIN

  mock     No network. Returns canned values so you can test the pipeline.

Config is read from environment variables, or from a local `tesla_config.json`
(git-ignored) of the same keys. Examples:

    export TESSIE_TOKEN=...; python3 fetch_tesla.py tessie
    python3 fetch_tesla.py mock --dry-run

A single reading is kept per date, so running it repeatedly in a day just
updates today's entry.
"""
import json
import os
import sys
import urllib.request
from datetime import date

from tesla_store import load, save, upsert_by_date

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "tesla_config.json")


def cfg(key, default=None):
    if key in os.environ:
        return os.environ[key]
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        if key in data:
            return data[key]
    return default


def _get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


# ---- backends: each returns {odometer, battery_level, battery_range_now} ----

def fetch_tessie(vin):
    token = cfg("TESSIE_TOKEN")
    if not token:
        raise SystemExit("Set TESSIE_TOKEN (env var or tesla_config.json).")
    # use_cache=true reads the last known state without waking the car.
    url = "https://api.tessie.com/%s/state?use_cache=true" % vin
    data = _get_json(url, {"Authorization": "Bearer " + token, "Accept": "application/json"})
    cs = data.get("charge_state", {})
    vs = data.get("vehicle_state", {})
    return {
        "odometer": round(vs["odometer"]),
        "battery_level": cs.get("battery_level"),
        "battery_range_now": cs.get("battery_range"),
    }


def fetch_fleet(vin):
    base = cfg("TESLA_FLEET_BASE")
    client_id = cfg("TESLA_CLIENT_ID")
    refresh = cfg("TESLA_REFRESH_TOKEN")
    if not (base and client_id and refresh):
        raise SystemExit("Fleet backend needs TESLA_FLEET_BASE, TESLA_CLIENT_ID, "
                         "TESLA_REFRESH_TOKEN. See https://developer.tesla.com.")
    # 1) refresh -> access token
    body = json.dumps({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh,
    }).encode()
    req = urllib.request.Request(
        "https://auth.tesla.com/oauth2/v3/token", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        access = json.load(resp)["access_token"]
    # 2) vehicle_data
    url = "%s/api/1/vehicles/%s/vehicle_data" % (base.rstrip("/"), vin)
    data = _get_json(url, {"Authorization": "Bearer " + access}).get("response", {})
    cs = data.get("charge_state", {})
    vs = data.get("vehicle_state", {})
    return {
        "odometer": round(vs["odometer"]),
        "battery_level": cs.get("battery_level"),
        "battery_range_now": cs.get("battery_range"),
    }


def fetch_mock(vin):
    return {"odometer": 78650, "battery_level": 72, "battery_range_now": 200}


BACKENDS = {"tessie": fetch_tessie, "fleet": fetch_fleet, "mock": fetch_mock}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}
    dry = "--dry-run" in flags or "-n" in flags

    backend = (args[0] if args else cfg("TESLA_BACKEND", "tessie")).lower()
    if backend not in BACKENDS:
        raise SystemExit("Unknown backend %r. Choose: %s" % (backend, ", ".join(BACKENDS)))

    text, start, end, obj = load()
    vin = cfg("TESLA_VIN") or obj["vehicle"].get("vin")
    if not vin and backend != "mock":
        raise SystemExit("No VIN. Set TESLA_VIN or vehicle.vin in data.js.")

    reading = BACKENDS[backend](vin or "MOCKVIN")
    today = str(date.today())
    odo = reading["odometer"]
    level = reading.get("battery_level")
    range_now = reading.get("battery_range_now")

    print("Fetched via %s: odometer=%s mi, battery=%s%%, range=%s mi"
          % (backend, odo, level, range_now))

    odo_entry = {"date": today, "odometer": odo, "note": "Auto (%s)" % backend}
    actions = [("odometer_readings", upsert_by_date(obj["odometer_readings"], odo_entry))]

    # Normalize the current range up to a 100%-charge equivalent for the
    # degradation trend (range_now is at the current charge level).
    if level and range_now:
        rated_100 = round(range_now / level * 100)
        bat_entry = {
            "date": today, "odometer": odo, "rated_range_100pct_mi": rated_100,
            "method": "%s @%s%%" % (backend.capitalize(), level),
            "note": "Extrapolated from %s mi @ %s%%" % (range_now, level),
        }
        actions.append(("battery_tests", upsert_by_date(obj["battery_tests"], bat_entry)))
        print("  -> battery test: %s mi @100%% (extrapolated)" % rated_100)

    if dry:
        print("\n[dry run] No changes written.")
        return

    save(text, start, end, obj)
    summary = ", ".join("%s %s" % (a, name) for name, a in actions)
    print("\n✓ Saved to data.js (%s). Refresh index.html." % summary)


if __name__ == "__main__":
    main()
