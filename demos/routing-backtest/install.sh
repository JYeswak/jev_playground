#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
cd "$root"
node --version
npm install --ignore-scripts --no-audit --no-fund --package-lock=false
npm test
printf 'jev-route-backtest ready: npm run backtest -- fixtures/real-excerpt-t1-t6.jsonl --out runs/backtest-real-excerpt.json\n'
