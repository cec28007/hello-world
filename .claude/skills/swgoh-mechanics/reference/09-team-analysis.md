# Team Analysis — "which direction to build, given my roster"

Individual-character advice isn't enough; what matters is **which teams** a roster
can field or is close to fielding, and which are worth finishing. This part of
the skill answers that by cross-referencing a curated meta-teams database against
a roster export.

## Honest note on "is there a definitive best-team resource?"

No single oracle exists. What exists is strong **community consensus**, captured
in tier lists and meta reports that shift with each patch:

- **swgoh.gg** — squad usage, GAC data, counters, roster browsing.
- **swgoh.wiki** — kits, factions, event requirements.
- **Content creators** — AhnaldT101, ljcool110, Warrior Presents, and others
  publish regular GAC/meta tier lists and farming guides.

The unique value here is **combining that consensus with the actual roster** — a
generic tier list can't tell you *which* team is your best next build. That's
what `tools/analyze_roster.py` + `data/meta_teams.json` do.

## The database: `data/meta_teams.json`

Each team entry has: `name`, `faction`, `leader` (base_id), `members`,
`alternates`, `modes` (`gac-def`, `gac-off`, `fleet`, `tw`, `raid`, `conquest`),
`tier` (S/A/B/C), and `notes`. It is a **seed** — expand it and re-verify tiers
against current tier lists periodically. Meta is patch-dependent; treat tiers as
a snapshot and flag that when advising.

## The tool: `tools/analyze_roster.py`

```
python3 analyze_roster.py <roster_export.json> [--mode gac-def] [--relic-floor 5]
```

Reads a swgoh.gg-style export (units with `base_id`, `rarity`, `gear_level`,
`relic_tier`, `combat_type`) and reports each team's readiness:

- **READY** — leader + core owned and at/above the relic floor → deployable now.
- **CLOSE** — missing one core unit (after alternates) OR some under the relic
  floor → the best *build-toward* candidates.
- **PROJECT** — missing two or more core units.
- **LOCKED** — missing the leader (the team can't function).

Results sort by readiness, then tier, so the highest-payoff, least-work teams
surface first. **Build-toward priority = CLOSE teams at S/A tier.**

### Notes / caveats
- **Ships** (`combat_type == 2`) have no relics — the tool judges them by star
  level (7★), not relic. Fleets read correctly as a result.
- **Relic values are raw export `relic_tier`**, offset from the in-game display;
  the tool compares them consistently (relative comparisons are valid). Tune
  `--relic-floor` to the bracket: 5 = baseline, 7 = GAC standard.
- Unowned units in build-toward teams correctly report as MISSING.

## How to use it in an answer

1. Run the tool on the latest roster export (filter by the mode the user cares
   about — usually `gac-def` for the "teams that hold" question).
2. Report the READY walls, then the CLOSE build-toward targets ranked by tier.
3. Tie back to the decision framework (`07`): CLOSE + S-tier + fixes a stated
   pain point (e.g., a GAC-defense hole) = the next project.
4. Flag any LOCKED team that needs a specific unlock (e.g., Inquisitors need
   Grand Inquisitor + Reva) so the user knows the gate.

## Example (Jaxen Sol, gac-def)

The current roster returns 9 READY defensive teams (3 GLs + Bounty Hunters,
Padmé GR, Mandalorians, Troopers, Resistance, Rebels) and 2 CLOSE S-tier
build-toward projects: **Great Mothers Nightsisters** (own the whole team, needs
gear/relics + star-ups on Great Mothers/Merrin) and **Clones** (elite once
**General Skywalker** leads). Inquisitors are LOCKED on the two missing leaders.
That directly answers "what should I build toward for GAC defense."
