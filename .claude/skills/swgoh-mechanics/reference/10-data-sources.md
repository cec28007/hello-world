# Data Sources — what can (and cannot) be pulled about a roster

Source-verified July 2026 (two research passes vs. swgoh-comlink, swgoh.help,
swgoh.gg, HotUtils docs/forums). This governs what advice can be roster-grounded
vs. what the player must tell us manually.

## The one architectural fact

Every **free** SWGOH data source (swgoh.gg, **swgoh-comlink**, swgoh.help) reads
the game's **public, unauthenticated surface** — i.e., exactly what you see when
you tap another player in-game. That surface **excludes**: unequipped mods,
unequipped gear, gear/relic materials, energy, GL Light/Dark tickets, and **all
currency balances (crystals, credits, tokens)**.

Only a tool that logs in **as the player** (EA account link / EAConnect) can reach
the private layer. Today that means **HotUtils** (paid, ToS-gray) — and even it
does not demonstrably surface currency *balances*.

## What each source exposes

| Source | Roster/mods/profile | Unequipped mods + gear inventory + salvage | Crystals/credits/energy/tickets | Auth | Cost | Automatable? |
|---|---|---|---|---|---|---|
| **swgoh.gg** (this repo's `fetch_swgoh.py`) | ✅ | ❌ | ❌ | public | free | ✅ (if domain allowlisted) |
| **swgoh-comlink** (self-host) | ✅ | ❌ | ❌ | none/guest | free | ✅ (Docker) |
| **swgoh.help** | ✅ | ❌ | ❌ | register | free | ✅ (migrating away) |
| **HotUtils** | ✅ | ✅ | ⚠️ **not surfaced** | **EA login** | **~$5–40/mo** | ❌ **no public API** — manual CSV/UI export only |

## What HotUtils actually buys you (verified)

- ✅ **Gear-piece inventory**, **relic/gear salvage**, and **full mod data**
  (including unequipped) — the genuine edge over swgoh.gg. Useful for "what can I
  gear/relic next" and mod planning.
- ⚠️ **Currency balances (crystals, credits, GET, GL tickets, energy): NO
  evidence it displays or exports these.** The bytes are in its authenticated
  payload, but it is not a surfaced/exported feature. **Do not expect crystal/
  credit numbers out of HotUtils.**
- ❌ **No programmatic API.** `api.hotutils.com` is private; no token flow, no
  public repos. Data leaves only via **website UI + CSV exports** (guild/roster
  CSV needs the ~$20 "Jalapeño" tier) or the HotBot Discord — **manual**.
- ⚠️ **ToS-gray.** Authenticates as you via EAConnect and can *write* to your
  account (push mod loadouts). Tolerated for years, no known mass bans, but **not
  sanctioned** — risk is the user's.

## Practical tiers (what to actually do)

1. **Free + automatable — roster layer.** Fix the swgoh.gg allowlist (or
   self-host comlink) so `fetch_swgoh.py` auto-pulls: full roster, equipped mods,
   **arena + fleet teams**, ranks, **GAC skill rating**, season stats. Covers most
   team/build advice. *(Currently blocked: environment proxy 403s swgoh.gg — needs
   allowlisting in the environment network policy.)*
2. **Paid + manual — inventory layer (optional).** HotUtils (~$20/mo Jalapeño)
   adds gear inventory + unequipped mods + salvage via **manual CSV export**
   committed to the repo. Worth it only if gear/mod *planning* matters to you.
3. **Manual — currency/energy layer (no tool).** Crystals, credits, GAC/Era
   currency, GL tickets, energy: **there is no data source.** The player records
   these by hand (a number or a screenshot). Store them in
   `data/manual_inputs.json` so any session reads them.

## Rule for advising

- Team/roster/mods/arena/fleet/GAC-rating questions → **roster export is enough.**
- Gear/relic "what can I finish" questions → need HotUtils export **or** ask.
- "Can I afford X / how many crystals/credits/tickets" → **must come from the
  player** (manual_inputs.json or ask). Never guess these.

## Sources
- [swgoh-comlink README](https://github.com/swgoh-utils/swgoh-comlink/blob/main/README.md) · [Player-Data wiki](https://github.com/swgoh-utils/swgoh-comlink/wiki/Player-Data)
- [api.swgoh.help](https://api.swgoh.help/) · [swgoh.gg](https://swgoh.gg/)
- [hotutils.com](https://hotutils.com/) · [EAConnect](https://hotutils.com/eaconnect) · [private API notice](https://api.hotutils.com/) · [Patreon tiers](https://www.patreon.com/hotutils)
- [EA Forums — HotUtils & ToS](https://forums.ea.com/discussions/swgoh-general-discussion-en/why-is-hotsauces-hotutils-not-against-tos/3579594)
