#!/bin/sh
set -eu
: "${SOURCE:?SOURCE must name the tracked hook}"
: "${TARGET:?TARGET must name the profile hook}"
node -e 'const fs = require("node:fs"); const a = fs.statSync(process.argv[1]); const b = fs.statSync(process.argv[2]); if (a.dev !== b.dev || a.ino !== b.ino) process.exit(1)' "$SOURCE" "$TARGET"
