#!/usr/bin/env python3
"""One-time setup helper for the Tesla Fleet API (free, personal use).

It does the two annoying one-time steps so `fetch_tesla.py fleet` can run
unattended afterwards:

    python3 tesla_auth.py partner    # register your domain with Tesla (once)
    python3 tesla_auth.py login      # OAuth -> save a refresh token

Both read these values from env vars or a git-ignored tesla_config.json:

    TESLA_CLIENT_ID       your app's client id   (developer.tesla.com)
    TESLA_CLIENT_SECRET   your app's client secret
    TESLA_DOMAIN          domain hosting your public key (e.g. tesla.example.com)
    TESLA_REDIRECT_URI    a redirect URI registered on your app
    TESLA_FLEET_BASE      optional; defaults to the North America base

`login` saves TESLA_CLIENT_ID + TESLA_REFRESH_TOKEN into tesla_config.json.
See docs/fleet-and-oracle.md for the full walkthrough.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "tesla_config.json")
AUTH_BASE = "https://auth.tesla.com/oauth2/v3"
FLEET_BASE_NA = "https://fleet-api.prd.na.vn.cloud.tesla.com"
SCOPES = "openid offline_access vehicle_device_data"


def cfg(key, default=None):
    if key in os.environ:
        return os.environ[key]
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as fh:
            if (v := json.load(fh).get(key)) is not None:
                return v
    return default


def require(*keys):
    vals = [cfg(k) for k in keys]
    missing = [k for k, v in zip(keys, vals) if not v]
    if missing:
        raise SystemExit("Missing config: " + ", ".join(missing)
                         + "\nSet env vars or add them to tesla_config.json.")
    return vals


def post_form(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def save_config(updates):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
    data.update(updates)
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print("Saved %s -> tesla_config.json" % ", ".join(updates))


def cmd_partner():
    """Register your domain so Tesla will fetch your hosted public key."""
    client_id, client_secret, domain = require(
        "TESLA_CLIENT_ID", "TESLA_CLIENT_SECRET", "TESLA_DOMAIN")
    base = cfg("TESLA_FLEET_BASE", FLEET_BASE_NA)
    tok = post_form(AUTH_BASE + "/token", {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": SCOPES,
        "audience": base,
    })["access_token"]
    body = json.dumps({"domain": domain}).encode()
    req = urllib.request.Request(
        base + "/api/1/partner_accounts", data=body,
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("Partner registration OK:")
        print(json.dumps(json.load(resp), indent=2))


def cmd_login():
    """Print the authorize URL, then exchange the pasted redirect for tokens."""
    client_id, client_secret, redirect = require(
        "TESLA_CLIENT_ID", "TESLA_CLIENT_SECRET", "TESLA_REDIRECT_URI")
    base = cfg("TESLA_FLEET_BASE", FLEET_BASE_NA)
    authorize = AUTH_BASE + "/authorize?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect,
        "scope": SCOPES,
        "state": "dashboard",
    })
    print("\n1) Open this URL, log in, and approve:\n\n   %s\n" % authorize)
    print("2) You'll be redirected to %s?code=...  (the page may 404 — that's fine)." % redirect)
    pasted = input("\n3) Paste the FULL redirected URL (or just the code) here:\n> ").strip()
    if "code=" in pasted:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query)["code"][0]
    else:
        code = pasted
    tokens = post_form(AUTH_BASE + "/token", {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect,
        "audience": base,
    })
    save_config({
        "TESLA_CLIENT_ID": client_id,
        "TESLA_REFRESH_TOKEN": tokens["refresh_token"],
        "TESLA_FLEET_BASE": base,
    })
    print("\n✓ Refresh token saved. Test with:  python3 fetch_tesla.py fleet --dry-run")


COMMANDS = {"partner": cmd_partner, "login": cmd_login}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in COMMANDS:
        raise SystemExit("Usage: python3 tesla_auth.py {partner|login}")
    COMMANDS[cmd]()


if __name__ == "__main__":
    main()
