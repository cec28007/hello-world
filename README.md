# Tesla Ownership Dashboard — 2019 Model 3 Performance

A zero-dependency dashboard for tracking your Tesla over its life: odometer,
battery degradation, service history, wheel/tire setups, and estimated resale
value — with cost-of-ownership and degradation visualized over time and clear
thresholds around the **100,000-mile** mark.

No build step, no server, no internet required. All charts are hand-drawn SVG.

## Open it

Just open **`index.html`** in any browser (double-click it). That's it.

## What you get

**KPI cards** at the top: current odometer, battery health %, average miles/year,
estimated value, total cost of ownership ($/yr and $/mi), projected date you'll
hit 100k miles, battery-warranty remaining, and total service spend.

**Charts**
- **Battery capacity vs. odometer** — rated range at 100% as a % of original
  (310 mi), with the **70% warranty floor** and the **100k-mile** line marked.
- **Mileage over time** — odometer by date, with a dashed projection out to
  100,000 miles at your current pace.
- **Value vs. cumulative cost** — estimated resale value against running total
  cost (depreciation + service) over time.
- **Cost per mile over time.**

**Tables & cards** — wheel/tire setups (with the active set flagged), the full
battery test log, and itemized service history with a running total.

Hover any point on a chart for the underlying numbers.

## Thresholds around 100,000 miles

The 100k line shows up on the battery and mileage charts, the odometer KPI
flags **"approaching 100k"** past 90k and **"100k+"** after, and a projection
estimates *when* you'll get there. For reference on a 2019 Model 3 Performance,
the battery & drivetrain warranty is **8 years / 120,000 miles** with a minimum
**70% capacity retention** — both are tracked.

## Adding a new data point

Two ways, pick whichever you like — both write to **`data.js`**:

**Guided (recommended):**
```bash
python3 add_entry.py            # interactive menu
python3 add_entry.py battery    # or jump straight to a category
```
Categories: `odometer`, `battery`, `service`, `resale`, `wheel`.

**By hand:** open `data.js` and add a row to the relevant list. It's plain JSON
inside `window.TESLA_DATA = { ... }`. Each list is documented by example.

Then refresh `index.html`.

## Pulling live data automatically (`fetch_tesla.py`)

Instead of typing readings in, you can pull the car's current odometer and
battery straight into `data.js`:

```bash
python3 fetch_tesla.py mock --dry-run   # try the pipeline, no network/credentials
python3 fetch_tesla.py tessie           # real pull via Tessie
```

It appends today's odometer reading and a battery test (the current range is
extrapolated to a 100%-charge equivalent so the degradation trend stays
consistent). Running it more than once a day **updates** today's entry rather
than piling up duplicates. Then refresh `index.html`.

### Choosing a backend

| Backend | Setup | Notes |
|---------|-------|-------|
| `tessie` | [Tessie](https://tessie.com) account → API token | **Easiest.** Paid service (free trial). One token, one request. |
| `fleet` | Tesla [developer app](https://developer.tesla.com) + paired virtual key | Official & free, but heavier setup. Marked experimental. |
| `mock` | none | Canned values for testing the pipeline offline. |

Note: Tesla retired the old open "Owner API", so live data now requires either
a third-party service (Tessie) or the official Fleet API. *TeslaMate* is another
option — a self-hosted app that logs your car to its own database — but it's a
full service to run, so it's only worth it if you already want that.

### Credentials

Set them as environment variables, or put them in a git-ignored
`tesla_config.json` next to the scripts:

```jsonc
// tesla_config.json  (never committed)
{
  "TESSIE_TOKEN": "your-token",
  "TESLA_VIN": "5YJ3E1EA0KF000000"
}
```

`TESLA_VIN` defaults to `vehicle.vin` in `data.js` if set there.

### Free, fully automated setup

For a free, hands-off pipeline — the official **Tesla Fleet API** running on an
**Oracle Always Free VM** that pulls daily and commits the data back — follow
the step-by-step runbook in **[`docs/fleet-and-oracle.md`](docs/fleet-and-oracle.md)**.
Helpers included:

- `tesla_auth.py partner` / `tesla_auth.py login` — one-time domain registration
  and OAuth to get a refresh token (saved to git-ignored `tesla_config.json`).
- `deploy/` — `gen-keys.sh` (Fleet API key pair), `Caddyfile` (serves the
  required public-key file over HTTPS), and a `systemd` service + timer
  (`run_fetch.sh`) that pulls daily and pushes `data.js`.

### Or just a simple cron

```bash
# every day at 8am
0 8 * * *  cd /path/to/repo && /usr/bin/python3 fetch_tesla.py fleet >> fetch.log 2>&1
```

## Data model (`data.js`)

| List | Tracks | Key fields |
|------|--------|-----------|
| `vehicle` | car + warranty/baseline facts | `purchase_price`, `original_rated_range_mi`, `battery_warranty_*` |
| `odometer_readings` | mileage over time | `date`, `odometer`, `note` |
| `battery_tests` | degradation | `date`, `odometer`, `rated_range_100pct_mi`, `method` |
| `service_history` | maintenance/repairs/tires | `date`, `odometer`, `category`, `description`, `cost`, `vendor` |
| `wheel_setups` | wheel/tire configs | `name`, `active`, `wheel`, `tire_brand`, `tire_size` |
| `resale_estimates` | value over time | `date`, `odometer`, `value`, `source` |

The shipped data is **realistic sample data** — replace it with your real
numbers (or wipe the lists and start logging).

## How battery health is measured

Charge to 100% and read the **rated range** shown on the display, then log it as
a `battery_tests` entry. Capacity % is computed as that range ÷ the original
310 mi. Do it the same way each time (same conditions) for a clean trend.

---

## Bonus: SWGOH roster fetch (`fetch_swgoh.py`)

Unrelated to the Tesla dashboard — a small, zero-dependency script that pulls a
**Star Wars: Galaxy of Heroes** player profile from the free
[swgoh.gg](https://swgoh.gg) public API using your ally code. It prints a
summary (name, level, guild, galactic power, roster counts, top characters) and
saves the full JSON response to `swgoh_data.json` (git-ignored).

```bash
python3 fetch_swgoh.py mock                  # offline demo, no network
python3 fetch_swgoh.py --ally 611-121-817    # real pull from swgoh.gg
python3 fetch_swgoh.py --ally 611121817 --units 15   # top 15 characters
python3 fetch_swgoh.py --ally 611-121-817 --dry-run  # print, don't save
```

**Guild data** is available too — `--guild` also pulls the guild for that
player (the guild id is read off their profile), and `--guild-id <id>` pulls a
specific guild on its own:

```bash
python3 fetch_swgoh.py --ally 611-121-817 --guild   # player + their guild
python3 fetch_swgoh.py --guild-id <guild-id> --units 20   # guild only
```

The guild summary lists member count, total galactic power, and the top members
by GP; the full response is saved to `swgoh_guild_data.json` (git-ignored).

The ally code can also come from `SWGOH_ALLY_CODE` (env var or a git-ignored
`swgoh_config.json`), and a guild id from `SWGOH_GUILD_ID`. The profile/guild
must be **public/synced on swgoh.gg** for data to come back.

**No outbound access to swgoh.gg?** (e.g. a sandbox with a restricted egress
policy) — the API is just a URL, so open it in a browser, save the JSON, and
render it offline with no network:

```bash
# Browser: open https://swgoh.gg/api/player/611121817/  → save as player.json
python3 fetch_swgoh.py --from-file player.json
python3 fetch_swgoh.py --from-file player.json --guild-from-file guild.json
cat player.json | python3 fetch_swgoh.py --from-file -    # or via stdin
```

| Backend | Setup | Notes |
|---------|-------|-------|
| `live` | none (just an ally code) | **Default.** Needs outbound access to `swgoh.gg`. |
| `mock` | none | Canned profile for testing the output offline. |

Note: this requires network access to `swgoh.gg`. In sandboxes/CI with a
restricted egress policy the request is rejected (HTTP 403 at the proxy) — run
it from an unrestricted network, or add `swgoh.gg` to the allowlist.
