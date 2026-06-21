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
