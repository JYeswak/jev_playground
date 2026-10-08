#!/bin/sh
set -eu
: "${TARGET:?TARGET must name the fixture log}"
node -e 'const fs = require("node:fs"); if ((fs.statSync(process.argv[1]).mode & 0o777) !== 0o600) process.exit(1)' "$TARGET"
