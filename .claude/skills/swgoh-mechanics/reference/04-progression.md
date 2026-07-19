# SWGOH Unit Progression Systems

*Source-verified reference on how characters and ships get stronger. Current as of
July 2026. Where the game changed recently (Era of Anniversary overhaul,
2025–2026), the newest verified values are used and older values flagged.*

---

## 1. Stars & Shards

A unit **unlocks at whatever star level you have enough shards for**, and the
**maximum is 7 stars**. Each star raises base stats and unlocks the next ability
tier / omega access.

| Star | Shards for that star | Cumulative |
|------|---------------------|-----------|
| 1★ | 10 | 10 |
| 2★ | 15 | 25 |
| 3★ | 25 | 50 |
| 4★ | 30 | 80 |
| 5★ | 65 | 145 |
| 6★ | 85 | 230 |
| 7★ | 100 | 330 |

**330 shards total = 7 stars.** ([swgoh.wiki – Character Shards](https://swgoh.wiki/wiki/Character_Shards))

**Shard sources:** battle nodes (Cantina, Hard-mode LS/DS/Fleet — energy-gated,
capped attempts/day); store shipments (Guild, Galactic War, Cantina, Squad Arena,
Fleet Arena, Guild Events); events/journeys/marquees.

**Shard Shop:** once a unit is 7★, further shards convert to **Shard Store
Tokens**, spendable for other units' shards. Ships use **Ship Blueprints** the
same way. ([swgoh.wiki – Ship Blueprints](https://swgoh.wiki/wiki/Ship_Blueprints))

---

## 2. Level & Gear

- **Level cap 85.** Most gear/ability work requires 85.
- **Gear tiers G1–G13.** Each level has slots filled with gear pieces/salvage,
  often crafted from lower components — the "gear grind." ([swgoh.wiki – Gear](https://swgoh.wiki/wiki/Gear))
- **G13 = "relic-ready."** Top gear tier; fully G13 unlocks the **Relic** track
  and the biggest single gear stat jump.
- **The Scavenger** (Cantina) converts surplus Gear + Signal Data into **Scrap**,
  used to build **Relic Amplifiers**. ([swgoh.wiki – Scavenger](https://swgoh.wiki/wiki/Scavenger))

---

## 3. Relics

Relics are the **post-G13 stat track** — the single largest raw-stat jump. A G13
unit is **Relic 0**; each tier adds large gains.

- **Displayed max is Relic 9 (R9).** R7 and R9 are the most impactful jumps.
  ([gaming-fans – Relics](https://gaming-fans.com/star-wars-goh/relics/), [swgoh-cantina – Relic](https://swgoh-cantina.com/en/glossary/relic))
- ⚠️ **Data-export offset:** swgoh.gg JSON exports store a raw `relic_tier` field
  that is **offset from the in-game displayed relic number** (raw tier counts G13
  as a couple of tiers in). When reading a roster export, treat `relic_tier`
  values as approximate/relative and confirm the displayed relic if precision
  matters. (This is why a "relic 12" in a raw export is not a literal in-game
  R12 — the displayed max is R9.)
- **2025 change — relics below 7★:** relic track can start at **4★/level 85**;
  **R3 needs 5★, R4 needs 6★, R5+ needs 7★.** ([swtorstrategies – Relics at 4 Stars](https://swtorstrategies.com/2025/07/swgoh-lightspeed-tokens-relic-changes.html))

**Materials** escalate sharply by tier (Carbonite Circuit Board → Bronzium Wiring
→ Chromium Transistor → Aurodium Heatsink → Electrium Conductor → Zinbiddle Card →
Aeromagnifier / Impulse Detector at the top). The rarest mats (R7→R9) are the main
end-game bottleneck. ([swgoh.wiki – Relic Amplifier](https://swgoh.wiki/wiki/Relic_Amplifier))

**Priority rule of thumb:** R5 = baseline for any unit you field · R7 = GAC
standard · R9 = top-priority units only (GLs, key counters, meta leaders).

---

## 4. Mods

Six per character — where the top-end of a roster is actually won or lost.

**Sets** (2- or 4-piece): Speed (+10%, 4pc), Offense (+15%, 4pc), Crit Damage
(+30%, 4pc), Health (+10%, 2pc), Defense (+25%, 2pc), Crit Chance (+8%, 2pc),
Potency (+15%, 2pc), Tenacity (+20%, 2pc). ([swgoh.wiki – Mods](https://swgoh.wiki/wiki/Mods))

**Shapes/slots & primary:** Square (Offense%), Arrow (Speed/Off%/Def%/Health%/
Prot%/Accuracy/Crit Avoid), Diamond (Defense%), Triangle (Crit Chance/Crit
Damage/Off%/Def%/Health%/Prot%), Circle (Health%/Prot%), Cross (Potency/Tenacity/
Off%/Def%/Health%/Prot%).

**Primary vs secondary:** one primary (scales to mod level 15); up to 4
secondaries that reveal/upgrade every +3 levels.

**⭐ Speed is the most important stat.** Turn order/frequency is governed by Speed;
acting first and more often compounds every other stat. Speed secondaries (and the
Speed arrow primary) are the most valued mod outcome — worth more than raw
offense/health.

**Leveling & slicing:** mods level to 15; **slicing** raises rarity (5-dot →
6-dot), increasing primaries/secondaries. Requires level 15 + 5-dot; equipping a
6-dot needs the character at **G12 + 7★**. Slicing/re-rolling is fueled by mod
challenges and **arena/GAC currency** — an ongoing sink even at end-game.

---

## 5. Abilities

Leveled with **Ability Materials**:
- **Omega** — standard "max out" material for most abilities. ([swgoh.wiki – Omega](https://swgoh.wiki/wiki/Ability_Material_Omega))
- **Zeta** — premium upgrade for **zeta-flagged** abilities; scarce; a major power
  gate.
- **Omicron** — top tier for **omicron-flagged** abilities. **Many omicrons only
  activate in a specific mode** (GAC, TW, TB, Conquest, Raids) and do nothing
  elsewhere. ([swgoh.wiki – Omicron](https://swgoh.wiki/wiki/Ability_Material_Omicron), [Omicron List](https://swgoh.wiki/wiki/Omicron_List))

**Prioritize:** zetas that complete a meta squad or GL requirement, then highest
multipliers on units you field. Omicrons **by the mode you play most** — a GAC/TW
omicron is worthless to a pure-TB player. ([swgoh.gg – Ability Report](https://swgoh.gg/stats/ability-report/))

---

## 6. Capital Ships & Ship Abilities

- **Capital Ship abilities** use **Prestige** material (levels 2→8); **~1,950
  Prestige** fully maxes one capital ship. ([swgoh.wiki – Prestige](https://swgoh.wiki/wiki/Prestige))
- **Non-capital ship abilities** use Ship Ability Materials (Mk I/II/III) from the
  Fleet Challenge and Cantina.
- **Reinforcement (RI) abilities** — the one-time entry ability; most ships want
  RI maxed to perform in the reinforcement slot. ([swgoh.gg – Reinforcements](https://swgoh.gg/news/ships-20-an-introduction-to-reinforcements/))

---

## 7. Datacrons

Squad-level buffs for **PvP/competitive modes** (mainly **GAC**, also TW). Grant
both **stat and mechanic (ability) bonuses** to characters matching the datacron's
targeted faction/tag — a datacron only helps squads that match. ([swgoh.gg – Datacrons](https://swgoh.gg/datacrons/))

- Built up in **levels**; deepest levels give powerful ability-altering effects for
  narrow factions — the "seasonal balance levers" that shape each GAC meta.
- **Seasonal/expiring (Jan 2026 change):** datacrons **release monthly and last 3
  months**, then phase out; reroll costs were lowered. **Datacron power is
  temporary** — invest reroll currency on datacrons that boost your *current* GAC
  squads within the active window. ([swtorstrategies – Datacron Adjustment](https://swtorstrategies.com/2026/01/swgoh-datacron-release-adjustment-monthly-sets.html))

---

## 8. Lightspeed Tokens (LSTs)

**Catch-up consumables** that **instantly raise an OWNED unit to a fixed
baseline** of star/gear/relic/level/ability. Introduced in the Era of Anniversary
update. ([swgoh.gg – LST](https://swgoh.gg/lst/))

| Tier | Level | Stars | Gear/Relic | Ability |
|------|-------|-------|-----------|---------|
| **Carbonite** | 85 | 3★ | Gear X | 3 |
| **Bronzium** | 85 | 4★ | Gear XII | 4 |
| **Chromium** | 85 | 5★ | Relic 1 | 5 |
| **Aurodium** | 85 | 6★ | Relic 3 | 6 |
| **Kyber** | 85 | 7★ | Relic 5 | 7 |

An LST **raises a unit up to** that baseline; it never downgrades a unit already
above it.

**Critical restrictions:**
- **Owned units only** — an LST **cannot unlock a unit you don't have**.
- **Eligibility is a fixed list** (usually faction/era-restricted) set at release
  and **never expanded** to later-released characters. → *Always check the token's
  eligible-unit list before spending.*
- **LSTs expire 6 months after acquisition.**

([swtorstrategies – Lightspeed Tokens](https://swtorstrategies.com/2025/07/swgoh-lightspeed-tokens-relic-changes.html), [EA Forums – New Item](https://forums.ea.com/blog/swgoh-game-info-hub-en/game-changes--new-item/12373006))

> ⚠️ The current live structure is **five tiers** (adds **Kyber** at top). Older
> tokens keep their original values; confirm exact baselines against the in-game
> token description, as these are periodically retuned.

---

## Sources
- [swgoh.wiki – Character Shards](https://swgoh.wiki/wiki/Character_Shards) · [Ship Blueprints](https://swgoh.wiki/wiki/Ship_Blueprints) · [Gear](https://swgoh.wiki/wiki/Gear) · [Scavenger](https://swgoh.wiki/wiki/Scavenger) · [Relic Amplifier](https://swgoh.wiki/wiki/Relic_Amplifier) · [Mods](https://swgoh.wiki/wiki/Mods) · [Omega](https://swgoh.wiki/wiki/Ability_Material_Omega) · [Omicron](https://swgoh.wiki/wiki/Ability_Material_Omicron) · [Omicron List](https://swgoh.wiki/wiki/Omicron_List) · [Prestige](https://swgoh.wiki/wiki/Prestige)
- [gaming-fans – Relics](https://gaming-fans.com/star-wars-goh/relics/) · [swgoh-cantina – Relic](https://swgoh-cantina.com/en/glossary/relic)
- [swtorstrategies – Relics/Lightspeed Tokens](https://swtorstrategies.com/2025/07/swgoh-lightspeed-tokens-relic-changes.html) · [Datacron Adjustment](https://swtorstrategies.com/2026/01/swgoh-datacron-release-adjustment-monthly-sets.html)
- [swgoh.gg – Datacrons](https://swgoh.gg/datacrons/) · [LST](https://swgoh.gg/lst/) · [Reinforcements](https://swgoh.gg/news/ships-20-an-introduction-to-reinforcements/) · [Ability Report](https://swgoh.gg/stats/ability-report/)
- [EA Forums – Game Changes + New Item](https://forums.ea.com/blog/swgoh-game-info-hub-en/game-changes--new-item/12373006)

*Verification notes: Relic displayed max (R9) cross-checked across sources; raw
data-export `relic_tier` is offset. LST five-tier structure and datacron
monthly/3-month cadence reflect 2025–2026 changes and supersede older
descriptions. Exact material quantities and LST baselines are periodically
retuned — confirm against live values for precision-critical use.*
