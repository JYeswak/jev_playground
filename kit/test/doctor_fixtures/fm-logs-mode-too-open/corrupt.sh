#!/bin/sh
set -eu
: "${TARGET:?TARGET must name the fixture log}"
chmod 0644 "$TARGET"
