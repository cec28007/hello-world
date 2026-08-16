# Skill data — canonical, persistent inputs

These files make the repo the single source of truth so any new session reads
current data instead of re-pasting. See `../reference/10-data-sources.md` for
what each source can/can't provide.

| File | What it is | How to refresh |
|------|-----------|----------------|
| `roster_snapshot.json` | Full swgoh.gg roster export (roster, mods, arena+fleet teams, ranks, GAC rating, season stats) | See **Roster** below |
| `manual_inputs.json` | Data NO tool exposes — crystals, credits, GAC/Era currency, GL Light/Dark tickets, energy, GAC placements | Edit by hand (or paste a screenshot and let Claude fill it) |
| `meta_teams.json` | Curated meta-teams database (kept in sync with `../reference/06-meta-teams.md`) | Edit as meta shifts |

## Refreshing the roster (`roster_snapshot.json`)

**Now (manual bridge):** open `https://swgoh.gg/api/player/611121817/` in a
browser, save the JSON, and replace `roster_snapshot.json` (or paste it to Claude
and it will commit it). This is the copy-paste step.

**To automate it (one-time fix):** the repo already has `fetch_swgoh.py` and a
`SessionStart` hook that auto-pulls by ally code — but the environment's network
policy currently **403-blocks swgoh.gg**. Allowlist `swgoh.gg` (and
`game-assets.swgoh.gg`) in the environment's network policy and the hook will
refresh this file automatically every session — no more copy-paste. (Alternative:
self-host `swgoh-comlink` and point the fetch at it.)

## Refreshing currencies (`manual_inputs.json`)

No data source provides these — record them by hand. Fastest path: screenshot the
in-game currency/shipment screens and paste them to Claude; it updates the file.
Keep the `as_of` dates current so staleness is visible.

## Using the data

```
# defaults to roster_snapshot.json:
python3 ../tools/analyze_roster.py --mode gac-def
```
Claude should read `manual_inputs.json` for any "can I afford / how many" question
and never guess currencies.
