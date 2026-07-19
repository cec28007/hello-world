---
name: swgoh-mechanics
description: >-
  Knowledge base and decision framework for Star Wars: Galaxy of Heroes (SWGOH /
  SWGoH). Use this WHENEVER the user asks about Star Wars Galaxy of Heroes —
  GAC (Grand Arena Championship), fleets/ships, Galactic Legends, Galactic
  Ascension and Light/Dark ticket farming, relics/gear/stars/mods, currencies
  (crystals, Era currency, Lightspeed tokens, GAC/Aurodium, guild stores),
  meta teams, defense vs offense setup, or "what should I farm/build/prioritize
  next." Consult the reference files here BEFORE answering from memory, because
  SWGOH mechanics and meta are patch-dependent and easy to get wrong. Also load
  the player profile to give roster-specific advice.
---

# SWGOH Game Mechanics — Skill

A source-verified knowledge base for **Star Wars: Galaxy of Heroes**, plus a
decision framework for answering "what should I do next" questions. Built
because SWGOH's mechanics (especially the Galactic Legend ticket/energy economy)
and its meta are patch-dependent — answering from memory produces mistakes.

## How to use this skill

1. **Identify the domain** of the user's question and open the matching
   reference file below. Do not answer mechanics questions from memory first —
   read the reference, then answer.
2. **For "what should I prioritize" questions**, read
   `reference/07-decision-framework.md`. It encodes the prioritization logic
   (GAC as the hub, multi-mode ROI, the energy-economy tradeoff).
3. **For roster-specific advice**, read `reference/08-player-profile.md` for the
   known player (Jaxen Sol, ally code 611121817). If a fresh roster export is
   provided, prefer it and update the profile.
4. **Flag date-sensitivity.** Anything in the meta / tier-list files is a
   snapshot; say so, and re-verify with the web (or `fetch_swgoh.py`) if the
   answer is high-stakes.

## Reference index

| File | Covers |
|------|--------|
| `reference/01-gac.md` | Grand Arena Championship: formats (5v5/3v3), board, **banner scoring**, defense holds, leagues/divisions/skill rating, rewards |
| `reference/02-fleets.md` | Fleets/ships: capital + reinforcements, crew-derived stats, capital ability leveling, **capital ship meta tier list** |
| `reference/03-galactic-legends.md` | GLs, Galactic Ascension, the **Light/Dark ticket & energy economy**, SLKR vs GL Rey |
| `reference/04-progression.md` | Stars/shards, gear/G13, **relics**, **mods** (speed!), zetas/omicrons, datacrons, **Lightspeed tokens** |
| `reference/05-currencies-economy.md` | Crystals, energy types, every store & currency, **Era currency**, resource priorities |
| `reference/06-meta-teams.md` | Current best **GAC defensive & offensive teams**, GL priority (snapshot — verify) |
| `reference/07-decision-framework.md` | **How to decide what to build/farm next** — the prioritization logic |
| `reference/08-player-profile.md` | Jaxen Sol's roster, active projects, and current plan |

## Core principles (the short version)

- **It's one roster, not separate tracks.** GAC, fleet, and Era ranking all run
  on the same roster. Investments that lift multiple modes win.
- **GAC is the hub.** Best currency, rewards roster depth, and a GAC-strong
  roster carries fleet/TW/raids. Prioritize it; treat fleet and Era as feeders.
- **Galactic Legends are the biggest single levers** — on offense AND as GAC
  defensive walls.
- **The energy economy has real tradeoffs.** Light/Dark GL tickets are earned by
  spending your finite regular energy on Light/Dark nodes — so they compete with
  each other AND with gear farming. See `03-galactic-legends.md`.
- **Verify before advising on high-stakes spends.** Don't send the user to farm
  the wrong thing.
