#!/bin/sh
set -eu
: "${TARGET:?TARGET must name the managed tool}"
mv "$TARGET" "$TARGET.fixture-backup"
