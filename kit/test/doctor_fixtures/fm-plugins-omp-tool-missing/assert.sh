#!/bin/sh
set -eu
: "${TARGET:?TARGET must name the managed tool}"
: "${EXPECTED_TEMPLATE:?EXPECTED_TEMPLATE must name the immutable template}"
node -e 'const fs = require("node:fs"); const target = process.argv[1]; const template = process.argv[2]; if (!fs.existsSync(target) || !fs.existsSync(target + ".fixture-backup") || !fs.readFileSync(target).equals(fs.readFileSync(template))) process.exit(1)' "$TARGET" "$EXPECTED_TEMPLATE"
