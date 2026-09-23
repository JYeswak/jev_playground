# Addendum to p6-wave1 (W2.1) — from pane 1 AmberWillow, same bead jev-deep-kit-8q7.5

foundation/gates.sh at 33fe6ae: 14 PASS, 3 RED. One red arm is in your B11 territory:
`bash scripts/selftest-pin-liveness.sh` -> 7 ok, 1 FAIL: "row pinned to a hot file exits 3 — wanted
rc=3 got rc=0". Pin liveness is the instrument that would tell you which retry predicates' pins
moved (W2.1(c)). Diagnose why the planted hot-file arm no longer fires BEFORE you use pin state in
W2.1(c) — a resurrection count built on a blind instrument is the exact failure W2.1 exists to catch.
Report the cause in honesty-census.md; do not edit the script in wave 1.
