#!/usr/bin/env bash
# Start the local Pokémon Showdown server for PokéJev Stage B.
# Installs our one custom format (Gen 9 OU Clock) into the pinned fork's config/ as an untracked file,
# then starts the server with its tracked config.js (forcetimer = true) on port 8000.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ps_dir="$here/../../pokemon-showdown"
want="e64915c0e"
have="$(git -C "$ps_dir" rev-parse --short=9 HEAD)"
[ "$have" = "$want" ] || { echo "pokemon-showdown is at $have, pinned $want" >&2; exit 2; }
grep -q '^exports.forcetimer = true;' "$ps_dir/config/config.js" || { echo "config.js lost forcetimer" >&2; exit 2; }
cp "$here/showdown/custom-formats.ts" "$ps_dir/config/custom-formats.ts"
cd "$ps_dir"
exec node pokemon-showdown start --no-security "${PORT:-8000}"
