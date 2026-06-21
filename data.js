/*
 * Tesla Ownership Data — single source of truth for the dashboard.
 * --------------------------------------------------------------------
 * Edit this file to add a new data point, then refresh index.html.
 * Everything is plain JSON inside the assignment below.
 *
 * Tips:
 *   - Dates are "YYYY-MM-DD".
 *   - "odometer" is whole miles.
 *   - Keep each list sorted oldest -> newest (the dashboard sorts anyway,
 *     but it keeps the file readable).
 *   - You can also run `python3 add_entry.py` for guided entry.
 *
 * The sample rows below are realistic placeholders — replace them with
 * your real numbers.
 */
window.TESLA_DATA = {
  "vehicle": {
    "name": "2019 Model 3 Performance",
    "year": 2019,
    "model": "Model 3",
    "trim": "Performance (AWD)",
    "color": "Midnight Silver Metallic",
    "vin": "",
    "purchase_date": "2019-06-15",
    "purchase_odometer": 10,
    "purchase_price": 21000,
    "original_rated_range_mi": 310,
    "original_usable_kwh": 75,
    "battery_warranty_years": 8,
    "battery_warranty_miles": 120000,
    "battery_warranty_capacity_pct": 70,
    "basic_warranty_years": 4,
    "basic_warranty_miles": 50000
  },

  "odometer_readings": [
    { "date": "2019-06-15", "odometer": 10,    "note": "Delivery" },
    { "date": "2020-06-01", "odometer": 11500, "note": "" },
    { "date": "2021-06-01", "odometer": 23000, "note": "" },
    { "date": "2022-06-01", "odometer": 35000, "note": "" },
    { "date": "2023-06-01", "odometer": 48000, "note": "" },
    { "date": "2024-06-01", "odometer": 60000, "note": "" },
    { "date": "2025-06-01", "odometer": 70000, "note": "" },
    { "date": "2026-06-15", "odometer": 78200, "note": "Latest reading" }
  ],

  "battery_tests": [
    { "date": "2019-06-15", "odometer": 10,    "rated_range_100pct_mi": 310, "method": "Display @ 100%", "note": "Baseline at delivery" },
    { "date": "2021-06-01", "odometer": 23000, "rated_range_100pct_mi": 298, "method": "Display @ 100%", "note": "" },
    { "date": "2023-06-01", "odometer": 48000, "rated_range_100pct_mi": 288, "method": "Display @ 100%", "note": "" },
    { "date": "2025-06-01", "odometer": 70000, "rated_range_100pct_mi": 281, "method": "Display @ 100%", "note": "" },
    { "date": "2026-06-15", "odometer": 78200, "rated_range_100pct_mi": 279, "method": "Display @ 100%", "note": "Most recent full charge" }
  ],

  "service_history": [
    { "date": "2020-08-10", "odometer": 13200, "category": "Maintenance", "description": "Tire rotation",                  "cost": 0,    "vendor": "DIY" },
    { "date": "2021-05-20", "odometer": 22100, "category": "Tires",       "description": "New summer set — Michelin PS4S", "cost": 1400, "vendor": "Discount Tire" },
    { "date": "2022-07-12", "odometer": 36500, "category": "Maintenance", "description": "Brake fluid flush",              "cost": 120,  "vendor": "Tesla Service" },
    { "date": "2023-09-05", "odometer": 50200, "category": "Repair",      "description": "12V battery replacement",        "cost": 150,  "vendor": "Tesla Mobile" },
    { "date": "2024-06-18", "odometer": 60800, "category": "Tires",       "description": "New summer set — Michelin PS4S", "cost": 1500, "vendor": "Discount Tire" },
    { "date": "2025-03-22", "odometer": 67400, "category": "Maintenance", "description": "Cabin + HEPA filter",            "cost": 60,   "vendor": "DIY" },
    { "date": "2025-11-08", "odometer": 74900, "category": "Repair",      "description": "Front control arm bushings",     "cost": 480,  "vendor": "Indy EV Shop" }
  ],

  "wheel_setups": [
    {
      "name": "Summer (stock Performance)",
      "active": true,
      "season": "Summer",
      "wheel": "20\" Performance Gray",
      "tire_brand": "Michelin Pilot Sport 4S",
      "tire_size": "235/35R20",
      "installed_date": "2024-06-18",
      "odometer_installed": 60800,
      "notes": "Stock staggered-look square setup"
    },
    {
      "name": "Winter",
      "active": false,
      "season": "Winter",
      "wheel": "18\" Tesla Aero (aftermarket)",
      "tire_brand": "Michelin X-Ice Snow",
      "tire_size": "235/45R18",
      "installed_date": "2025-11-08",
      "odometer_installed": 74900,
      "notes": "Swapped on for the cold months; quieter ride"
    }
  ],

  "resale_estimates": [
    { "date": "2020-06-01", "odometer": 11500, "value": 20000, "source": "KBB private party" },
    { "date": "2021-06-01", "odometer": 23000, "value": 19000, "source": "KBB private party" },
    { "date": "2022-06-01", "odometer": 35000, "value": 18000, "source": "KBB private party" },
    { "date": "2023-06-01", "odometer": 48000, "value": 16500, "source": "KBB private party" },
    { "date": "2024-06-01", "odometer": 60000, "value": 15500, "source": "KBB private party" },
    { "date": "2025-06-01", "odometer": 70000, "value": 14500, "source": "KBB private party" },
    { "date": "2026-06-15", "odometer": 78200, "value": 13500, "source": "KBB private party" }
  ]
};
