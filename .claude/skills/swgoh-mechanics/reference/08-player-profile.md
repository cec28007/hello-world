# Player Profile — Jaxen Sol

Roster-specific context for giving tailored advice. Update this whenever a fresh
roster export (swgoh.gg JSON) is provided.

- **Name / ally code:** Jaxen Sol — `611121817`
- **Canonical data (committed to the repo):**
  `data/roster_snapshot.json` (full swgoh.gg export, updated 2026-07-19) and
  `data/manual_inputs.json` (currencies/tickets no tool exposes). Read BOTH for
  roster-grounded advice. `tools/analyze_roster.py` defaults to the snapshot.
  Live auto-refresh is blocked until swgoh.gg is allowlisted in the environment
  network policy — see `data/README.md`.
- **Account:** ~7.46M GP total · ~4.66M character GP · ~2.79M ship GP · Level 85
- **GAC:** Carbonite league, Division 2, skill rating ~2034
- **Fleet Arena rank:** ~74 · **Squad Arena rank:** ~111
- **Guild:** Honor Warriors

## Stated goals & pain points

- Wants to **rank higher in GAC** (and understand fleet/Era ranking).
- Recurring frustration: **losing GAC matches by ~1 point** after both players
  fully clear — i.e., losing the banner-efficiency tiebreak. **Fix = defensive
  walls that HOLD** (see decision framework + meta teams).

## Galactic Legends

| GL | State | Role |
|----|-------|------|
| **Leia Organa (GL)** | 7★ **R12** | Strongest single unit; top defensive wall (Rebels) |
| **Rey (GL)** | 7★, high relic (raw export `relic_tier` ~10 → offset; confirm displayed relic). **NOT fully maxed — Ultimate incomplete:** "Heir to the Light Side" screenshot shows *Journey in Progress*, Tier VI open, ~5 battles left | Best pure defensive-hold GL owned (Resistance). Finishing her **Ultimate** (Tier VI, light-side currency) is a real upgrade, not busywork |
| **Jedi Master Luke (JML)** | 7★ **R8** | Best *offensive* GL owned (Jedi) |
| **Supreme Leader Kylo Ren (SLKR)** | **In progress** — unlock journey started (0/330), Tier I requirements met | 4th GL; First Order |

**GL placement plan:** Rey + Leia on **defense** (walls), JML on **offense**.
SLKR adds a 4th GL / more flexibility once unlocked.

### SLKR unlock status (First Order requirement squad)
Requirement units are in great shape — mostly **relic 7-9**, at or above unlock
needs. Known gap: **Sith Trooper is 6★** (needs 7★ for a later tier). Kylo Ren
(Unmasked) R9, Kylo Ren R9, First Order Executioner R8, Hux/Phasma/Officer/
Stormtrooper/TIE Pilot/SF TIE Pilot all R7. → Not a long gear grind; the
remaining work is **farming Dark-side tickets** to run the Ascension tiers, plus
Sith Trooper to 7★ for the upper tiers.

## Fleets (all three are meta-relevant)

| Capital | State | Use |
|---------|-------|-----|
| **Profundity (Raddus)** | 7★, but **capital abilities half-leveled** — Holdo Maneuver 2/8, Recharge Deflectors 4/8, Outlast 4/8, Ace Maneuver 6/8 | **Offense** — best offensive fleet once abilities maxed |
| **Negotiator** | 7★, **all abilities 8/8 (maxed)** | **Defense** — sticky holder |
| **Endurance** | 7★, **all abilities 8/8 (maxed)** | Flex / 2nd defense |
| Finalizer / Chimaera / Executrix / Home One | Lower tier; Home One abilities only 2/8 | Bench / skip for GAC |

- **Profundity crew (Bounty Hunters):** Bossk R10, Han/Chewie/C-3PO (Han's Falcon)
  R7-9, Boba R7, Cad Bane R7 — but **IG-88 is R2** (limits IG-2000). Dengar R2.
- **#1 fleet fix:** level Profundity's capital abilities (esp. Holdo Maneuver
  2/8 → 8/8). Cheap, huge, lifts both Fleet Arena and GAC fleet.

## Defensive walls available (non-GL)

Deep roster — 108 non-GL units at R5+. **Corrected against `06-meta-teams.md`
(community data), which overturns earlier advice:**

- **Galactic Republic (Padmé lead)** — ✅ **READY genuine wall.** Protection-up /
  buff-immunity stall. This is the best non-GL wall you can field *today*.
- **Great Mothers Nightsisters** — 🔨 top S-tier build (own all; gear/relic +
  star Great Mothers/Merrin). Best non-GL wall once built.
- **Clones (General Skywalker lead)** — 🔨 S-tier build; needs **GAS** (6★ g12 r1
  → 7★ + relic). Rex/Echo-lead clones without GAS are only a B wall.
- **Inquisitors** — mid (B) wall; LOCKED on Grand Inquisitor + Reva.
- ❌ **Bounty Hunters (Bossk) are NOT a defensive wall** — Bossk gives no opening
  speed and gets CC'd/bursted. **Use BH on OFFENSE.** (Corrects earlier advice.)
- ❌ **Beskar-Mando lead Mandalorians / Range-Trooper Imperial Troopers are NOT
  meta walls.** The real versions need **Bo-Katan (Mand'alor)** (not owned) and
  **Iden Versio** (owned only 4★ g1) — neither is fieldable now.
- **Resistance / CLS Rebels** — only B/situational walls; GL Leia is the real
  Rebel wall.

> Run `tools/analyze_roster.py --mode gac-def` on the latest export for the live
> READY / CLOSE / LOCKED breakdown.

## Key build projects (ranked)

1. **Finish SLKR** — farm Dark-side tickets; Sith Trooper → 7★. Biggest lever.
2. **Finish Profundity capital abilities** — cheapest high-impact fleet fix.
3. **Great Mothers Nightsisters** — owns the ENTIRE team (Great Mothers 4★ g1,
   Merrin 3★ g1, Mother Talzin/Old Daka/Nightsister Zombie 7★ but r1, Asajj r7
   as ready alt). Top non-GL defensive wall; just needs gearing. Best 5:
   **Great Mothers (L) · Merrin · Mother Talzin · Old Daka · Nightsister Zombie**
   (Asajj = swap). This directly fixes the "lose GAC by 1" problem.
4. **Inquisitors** (2nd wall) — owns 5 at 7★ g13 (Second/Fifth/Eighth/Ninth/
   Seventh Sister-Brother, all r2) + Marrok r5, but **missing both leaders:
   Grand Inquisitor and Third Sister (Reva)** — must be unlocked before the team
   functions. Tokens can't unlock un-owned units.

## Resources

- **Era Currency:** ~34.7K / 150K cap — buys **Lightspeed Tokens** (Aurodium
  ~3,500, Carbonite ~1,000) in the Era Shipment. Best use: **star-hungry, meta
  units** (e.g., Great Mothers / Merrin) **if they appear in the current token's
  eligible list** (rotates by Era — verify before spending). Spend Aurodium
  (higher tier) on the units needing the biggest jump.
- Owns a partial **Spectre** Lightspeed-token pool (Ahsoka Fulcrum at lvl1 g1 was
  a prime target).

## Standing recommendations (the plan)

- **Defense:** Rey + Leia (GL walls) + **Padmé GR** (ready non-GL wall); build
  **Great Mothers Nightsisters** (marquee) and **GAS Clones** as the next walls.
- **Offense:** Profundity (finish abilities) + JML for the hard team + **Bounty
  Hunters (Bossk)**; deep relic squads clear the rest with **zero-death** clears
  (retreat/retry messy fights).
- **Farming focus:** Dark-side tickets for SLKR (on nodes that also drop needed
  gear); daily arena climbs for crystals; Era tokens into Great Mothers/Merrin.
