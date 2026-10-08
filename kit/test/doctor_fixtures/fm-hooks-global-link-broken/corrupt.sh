#!/bin/sh
set -eu
: "${SOURCE:?SOURCE must name the tracked hook}"
: "${TARGET:?TARGET must name the copied profile hook}"
cp "$SOURCE" "$TARGET"
