#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
cd "$root"
node --version
npm install --ignore-scripts --no-audit --no-fund --package-lock=false
npm test
printf 'jev-route-backtest ready: npm run backtest -- <session.jsonl>... --out runs/backtest.json\n'
