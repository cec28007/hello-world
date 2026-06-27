#!/bin/bash
# SessionStart hook: auto-load the current SWGOH roster so Claude always has
# fresh data when a session begins. Read-only and best-effort — if swgoh.gg
# isn't reachable (e.g. the environment's network policy hasn't allowlisted
# it yet) the fetch is skipped and the session still starts cleanly.
set -uo pipefail

# Only bother in remote (Claude Code on the web) sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ALLY="${SWGOH_ALLY_CODE:-611121817}"   # public ally code; override via env
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if python3 fetch_swgoh.py --ally "$ALLY" --guild >/tmp/swgoh_fetch.log 2>&1; then
  echo "SWGOH roster loaded for ally ${ALLY} (swgoh_data.json + swgoh_guild_data.json are ready to read)."
else
  echo "SWGOH auto-fetch skipped: swgoh.gg was not reachable. To enable live pulls, allowlist swgoh.gg in this environment's network policy. (log: /tmp/swgoh_fetch.log)"
fi
exit 0
