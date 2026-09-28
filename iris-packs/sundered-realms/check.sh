#!/usr/bin/env bash
# Rebuilds the pack and validates it offline against the current Iris engine source.
#   ./check.sh [overworld-pack-folder]
# Without an argument the official overworld pack (tag OVERWORLD_TAG) is cloned from GitHub.
# The engine schema comes from Iris tag IRIS_TAG. Set WORK=<dir> to reuse a work directory.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$(mktemp -d)}"
BASE="${1:-}"
IRIS_TAG="${IRIS_TAG:-4.0.1-26.1.2-26.2}"
OVERWORLD_TAG="${OVERWORLD_TAG:-4002}"

[ -d "$WORK/Iris" ] || git clone --depth 1 --branch "$IRIS_TAG" https://github.com/VolmitSoftware/Iris.git "$WORK/Iris"
if [ -z "$BASE" ]; then
  [ -d "$WORK/overworld" ] || git clone --depth 1 --branch "$OVERWORLD_TAG" https://github.com/IrisDimensions/overworld.git "$WORK/overworld"
  BASE="$WORK/overworld"
fi

python3 "$HERE/tools/schema.py" "$WORK/Iris/core/src/main/java" "$WORK/schema.json"
python3 "$HERE/tools/build_objects.py"
python3 "$HERE/tools/build_pack.py" --base "$BASE"
"$HERE/install.sh" "$BASE" "$WORK/server" --force >/dev/null
python3 "$HERE/tools/validate.py" "$WORK/schema.json" "$WORK/server/plugins/Iris/packs/sundered-realms" \
  biomes/sundered regions/sundered dimensions generators/sundered loot/sundered spawners/sundered entities/sundered
