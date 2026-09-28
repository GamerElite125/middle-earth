#!/usr/bin/env bash
# Rebuilds the pack and validates it offline against the current Iris engine source.
#   ./check.sh [overworld-pack-folder]
# Without an argument the official overworld pack is cloned from GitHub.
# Set WORK=<dir> to reuse a work directory between runs.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$(mktemp -d)}"
BASE="${1:-}"

[ -d "$WORK/Iris" ] || git clone --depth 1 https://github.com/VolmitSoftware/Iris.git "$WORK/Iris"
if [ -z "$BASE" ]; then
  [ -d "$WORK/overworld" ] || git clone --depth 1 https://github.com/IrisDimensions/overworld.git "$WORK/overworld"
  BASE="$WORK/overworld"
fi

python3 "$HERE/tools/schema.py" "$WORK/Iris/core/src/main/java" "$WORK/schema.json"
python3 "$HERE/tools/build_objects.py"
python3 "$HERE/tools/build_pack.py" --base "$BASE"
"$HERE/install.sh" "$BASE" "$WORK/server" --force >/dev/null
python3 "$HERE/tools/validate.py" "$WORK/schema.json" "$WORK/server/plugins/Iris/packs/sundered-realms" \
  biomes/sundered regions/sundered dimensions generators/sundered loot/sundered spawners/sundered entities/sundered
