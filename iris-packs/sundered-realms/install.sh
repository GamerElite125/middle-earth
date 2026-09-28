#!/usr/bin/env bash
# Installs the Sundered Realms Iris pack on top of an Iris "overworld" pack.
#   ./install.sh <overworld-pack-folder> <server-folder> [--force]
# The overworld folder is only read, never modified.
set -euo pipefail

SRC="${1:?usage: install.sh <overworld-pack-folder> <server-folder> [--force]}"
SERVER="${2:?usage: install.sh <overworld-pack-folder> <server-folder> [--force]}"
FORCE="${3:-}"
PACK_NAME="sundered-realms"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$SERVER/plugins/Iris/packs/$PACK_NAME"

if [ ! -f "$SRC/dimensions/overworld.json" ]; then
  nested="$(find "$SRC" -mindepth 2 -maxdepth 3 -path '*/dimensions/overworld.json' | head -n1 || true)"
  [ -n "$nested" ] || { echo "No dimensions/overworld.json under $SRC" >&2; exit 1; }
  SRC="$(dirname "$(dirname "$nested")")"
fi
if [ -e "$DEST" ]; then
  [ "$FORCE" = "--force" ] || { echo "$DEST exists; re-run with --force to replace it" >&2; exit 1; }
  rm -rf "$DEST"
fi
mkdir -p "$DEST"
echo "Copying base overworld pack from $SRC ..."
(cd "$SRC" && tar --exclude=.git --exclude=.github -cf - .) | (cd "$DEST" && tar -xf -)
echo "Overlaying Sundered Realms content ..."
cp -R "$HERE/pack/." "$DEST/"
rm -f "$DEST/dimensions/overworld.json"
echo
echo "Installed to $DEST"
echo "Create a world with:  /iris create name=aerthos type=$PACK_NAME"
