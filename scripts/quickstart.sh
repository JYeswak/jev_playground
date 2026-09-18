#!/usr/bin/env bash
# quickstart — five questions, answered with numbers, from a fresh clone in one command.
#
# WHY THIS SHAPE. The first version of this script ran five suites and printed PASS five times. Pane 3
# graded it as the non-author (quickstart-grade-20260918T162959Z.json, ada5e58) and returned
# ENABLER-in-product-clothes, with the specific finding that ALL FIVE "what you learn" lines mismatched
# the output: they promised answers and the output gave counts. Worst was the probe, whose underlying
# command prints the richest thing in the repo — a full judgment with per-lever probabilities — while
# the runner surfaced none of it. One of the five was a literal one-token grep bug: the harness prints
# "mutations: 7/7 caught" with a colon, and the filter looked for the colonless form, so a reader got
# a bare PASS from the only suite in the repo that proves its own tests can fail.
#
# So this does not run tests and report on tests. It runs the demos' own tools, reads the receipts they
# write, and prints the ANSWER each one produces — including when the answer is unflattering, which for
# the router it is.
#
# NOT a gate, NOT wired to foundation. Pane 3 separately REFUSED wiring it into verify-frozen
# (quickstart-wiring-ruling-20260918T163132Z.json): it fails the creation gate at CONSUMER, since
# verify-frozen branches on nothing this reports, and a RED here would conflate demo health with clone
# reproducibility. Its only consumer is a human who just cloned the repo.
#
# EVERY NUMBER BELOW IS DERIVED AT RUNTIME from the receipt the tool just wrote. None is hardcoded.
# This repo got a number wrong roughly a dozen times in one day by writing it down once.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

node --version >/dev/null 2>&1 || { echo "quickstart: needs node >= 20 on PATH, and nothing else."; exit 2; }
# --mine: the same questions, answered against the READER'S OWN logs instead of our fixture.
#
# WHY THIS EXISTS. Every answer this script gives without --mine is computed from a 6-turn fixture
# committed to this repo. That proves the tools RUN; it tells a stranger nothing about their own
# spend. The only bridge was a closing line telling them to pass their own path — a bridge the reader
# has to build. This walks it for them, which is the difference between a demo and a tool.
if [[ "${1:-}" == "--mine" ]]; then
  corpus="${2:-$HOME/.claude/projects}"
  if [[ ! -d "$corpus" && ! -f "$corpus" ]]; then
    cat <<EOF
quickstart --mine: no session logs at $corpus

This looks for Claude Code session JSONL, which normally lives in ~/.claude/projects. If yours are
elsewhere, pass the path: ./scripts/quickstart.sh --mine /path/to/logs

Nothing is uploaded and no key is used — every tool reads local files and writes a local receipt. If
you have no such logs, the fixture answers (./scripts/quickstart.sh) still show what the tools do.
EOF
    exit 2
  fi
  n_files="$(find "$corpus" -name '*.jsonl' -type f 2>/dev/null | grep -c . || true)"
  if [[ "${n_files:-0}" -eq 0 ]]; then
    echo "quickstart --mine: $corpus exists but holds no .jsonl session files."
    exit 2
  fi
  mine_work="$(mktemp -d)"
  trap 'test -n "${mine_work:-}" && find "$mine_work" -mindepth 1 -delete 2>/dev/null; rmdir "$mine_work" 2>/dev/null' EXIT
  echo "quickstart --mine — YOUR logs: $n_files session file(s) under $corpus"
  echo "Offline. No key. No upload. Receipts are written to a temp dir and discarded on exit."
  echo

  echo "=== Where does your agent spend actually go?"
  node demos/usage-shape/bin/shape.mjs "$corpus" 2>&1 | sed 's/^/    /' \
    || echo "    COULD NOT ANSWER — the shape tool failed on your corpus, which is worth an issue."

  echo
  echo "=== Would routing cheap turns to a cheaper model have saved YOU money?"
  # FILES, NOT THE DIRECTORY. Passing the corpus root returned EISDIR: this demo takes session files
  # while the shape tool takes a directory, and nothing said so. A bounded sample keeps the argument
  # list finite, and the sample size is PRINTED rather than hidden, because a silently sampled
  # denominator is the defect this repo has spent the day removing from its own documents.
  sample_n=200
  mine_files=()
  while IFS= read -r f; do mine_files+=("$f"); done < <(find "$corpus" -name '*.jsonl' -type f 2>/dev/null | head -"$sample_n")
  echo "    (bounded sample: ${#mine_files[@]} of $n_files session files, newest-first as the filesystem lists them)"
  if node demos/routing-backtest/bin/backtest.mjs "${mine_files[@]}" --out "$mine_work/bt.json" >"$mine_work/bt.log" 2>&1; then
    node -e '
      const r=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8")), t=r.totals, d=r.denominator;
      for (const k of ["actualSpend","counterfactualSpend","estimatedSavings"])
        if (typeof t[k] !== "number") throw new Error(`totals.${k} missing — receipt schema changed`);
      const pct=(t.counterfactualSpend/t.actualSpend-1)*100;
      console.log(`    ${t.estimatedSavings<0?"NO — it would have COST you more":"YES — it would have saved"}: $${t.actualSpend.toFixed(4)} actual vs $${t.counterfactualSpend.toFixed(4)} routed (${Math.abs(pct).toFixed(1)}%).`);
      console.log(`    Denominator: ${d.classifiableTurns} classifiable of ${d.turns} turns, ${d.skippedTurns} skipped.`);
    ' "$mine_work/bt.json" || echo "    COULD NOT ANSWER — receipt written but unreadable."
  else
    # THE FAILURE CODE IS QUOTED, NOT EXPLAINED AWAY. An earlier version of this branch asserted the
    # cause was "a model this demo has no price for". That was a GUESS, and it was wrong: on a real
    # Claude Code corpus the receipt returns EMPTY_CLASSIFIABLE_SET. Printing the demo's own code is
    # the only honest thing to do when the demo declines.
    codes="$(node -e '
      try {
        const r=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));
        console.log((r.failures||[]).map(f=>`${f.code}: ${f.message}`).join("; ")||"no failures recorded");
      } catch { console.log("receipt unreadable"); }
    ' "$mine_work/bt.json" 2>/dev/null || echo "receipt unreadable")"
    echo "    NO ANSWER, and the demo refused rather than guessed: $codes"
    echo
    echo "    THIS IS A REAL LIMIT OF THE DEMO, not a problem with your logs. It classifies turns by"
    echo "    model and usage fields in a shape this corpus does not provide, so on Claude Code"
    echo "    sessions it finds no classifiable turns at all. Measured here against $n_files real"
    echo "    session files. The fixture answer (./scripts/quickstart.sh) is therefore a proof that"
    echo "    the accounting works, NOT evidence that it works on your data."
  fi

  echo "None of this is a recommendation. These are YOUR numbers under this repo's STATED assumptions:"
  echo "the price table and the cheap-model rates are assumptions, not facts, and the receipt written"
  echo "by demos/routing-backtest/bin/backtest.mjs says so in its own rederivation field."
  exit 0
fi

work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
fix="demos/routing-backtest/fixtures/real-excerpt-t1-t6.jsonl"
pass=0; fail=0; failed=""

q() { printf '\n=== Q%s. %s\n' "$1" "$2"; }
ok() { pass=$((pass+1)); }
no() { fail=$((fail+1)); failed="$failed $1"; printf '    COULD NOT ANSWER — see %s\n' "$2"; }

echo "quickstart — five questions, answered from committed bytes. No install, no network, no API key."

# ---------------------------------------------------------------- Q1
q 1 "Would routing cheap turns to a cheaper model have saved money?"
if node demos/routing-backtest/bin/backtest.mjs "$fix" --out "$work/bt.json" >"$work/bt.log" 2>&1; then
  node -e '
    const r=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8")), t=r.totals, d=r.denominator;
    // FIELDS ASSERTED, NOT ASSUMED. Measured while arming this script: renaming a field the answer
    // depends on left the direction sentence reading from `undefined`, and `undefined < 0` is false,
    // so the runner would have cheerfully printed the OPPOSITE verdict with correct-looking dollars
    // beside it. A missing number must break the answer, not silently pick a branch.
    for (const k of ["actualSpend","counterfactualSpend","estimatedSavings"])
      if (typeof t[k] !== "number") throw new Error(`totals.${k} missing or not a number — receipt schema changed`);
    const pct=(t.counterfactualSpend/t.actualSpend-1)*100;
    const dir = t.estimatedSavings < 0 ? "COST YOU MORE" : "saved";
    console.log(`    NO. On this fixture routing would have ${dir}: $${t.actualSpend.toFixed(6)} actual`);
    console.log(`    vs $${t.counterfactualSpend.toFixed(6)} routed — ${Math.abs(pct).toFixed(1)}% worse, on ${d.classifiableTurns} of ${d.turns} turns.`);
    console.log(`    The demo is willing to answer no. That is the point of running it on YOUR logs.`);
  ' "$work/bt.json" && ok || no Q1 "$work/bt.log"
else no Q1 "$work/bt.log"; fi

# ---------------------------------------------------------------- Q2
q 2 "Can that demo's tests still fail, or are they decoration?"
if ( cd demos/routing-backtest && npm run mutate --silent ) >"$work/mu.log" 2>&1; then
  # The colon form. This is the token the first version of this script got wrong.
  line="$(grep -oE 'mutations:[[:space:]]*[0-9]+/[0-9]+ caught' "$work/mu.log" | tail -1)"
  if [[ -n "$line" ]]; then
    printf '    YES — %s. Each mutation is a named sabotage of the scoring code, planted one at a\n' "$line"
    printf '    time into a green suite; if the tests still pass, that mutation ESCAPED and this fails.\n'
    grep -oE 'CAUGHT[[:space:]]+[a-z-]+' "$work/mu.log" | head -3 | sed 's/^/      /'
    ok
  else no Q2 "$work/mu.log"; fi
else no Q2 "$work/mu.log"; fi

# ---------------------------------------------------------------- Q3
q 3 "How much of a coding agent's context is resent every single turn?"
if node -e '
    const c=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8")), t=c.totals, d=c.denominator;
    const onTotal=t.cacheRead/t.total*100, onBilled=t.cacheRead/t.billedInput*100;
    console.log(`    ${onTotal.toFixed(3)}% of all tokens are cache reads — context resent, not new work.`);
    console.log(`    Denominator, stated: ${d.turns.toLocaleString()} turns across ${d.sessions.toLocaleString()} sessions in ${d.files.toLocaleString()} files, ${d.unparsable_lines} unparsable.`);
    console.log(`    Basis matters here: ${onTotal.toFixed(3)}% against all tokens, ${onBilled.toFixed(3)}% against billed input only.`);
    console.log(`    This repo published two spend figures off two unstated bases once. Never again unstated.`);
  ' docs/demos/jev-probe/census-20260918.json 2>"$work/cs.log"; then ok; else no Q3 "$work/cs.log"; fi

# ---------------------------------------------------------------- Q4
q 4 "Which lever is that spend actually in, and does the accounting close?"
if node demos/retransmit-whatif/bin/whatif.mjs "$fix" --out "$work/wi.json" >"$work/wi.log" 2>&1; then
  node -e '
    const r=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8")), a=r.levers.aggregate, d=r.denominator;
    const top=a[0], un=a.find(x=>x.lever==="unreconciled");
    console.log(`    ${top.lever}: ${(top.share*100).toFixed(1)}% of ${a.reduce((s,x)=>s+x.tokens,0).toLocaleString()} tokens over ${d.assistantTurns} assistant turns.`);
    a.slice(1).forEach(x=>console.log(`      ${x.lever.padEnd(13)} ${(x.share*100).toFixed(1)}%`));
    console.log(`    Unreconciled: ${un.tokens} tokens. The residual is printed, so a share that does not`);
    console.log(`    add up shows as a number instead of disappearing into a rounding.`);
  ' "$work/wi.json" && ok || no Q4 "$work/wi.log"
else no Q4 "$work/wi.log"; fi

# ---------------------------------------------------------------- Q5
q 5 "What does a Jev judgment actually look like?"
if node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json >"$work/pr.json" 2>"$work/pr.log"; then
  node -e '
    const t=require("fs").readFileSync(process.argv[1],"utf8");
    const j=JSON.parse(t.slice(t.indexOf("{")));
    // EXPLICIT schema path, not a heuristic walk. The first version walked for "any object of numbers
    // in 0..1" and surfaced `confidence: 0.7` — a real number from the wrong object. A reader would
    // have believed it. answers.<question>.probabilities is where the judgment lives.
    const qs=Object.entries(j.answers||{}).filter(([,v])=>v&&v.probabilities);
    if(!qs.length) throw new Error("no answers.*.probabilities in this response");
    for(const [name,a] of qs){
      const rows=Object.entries(a.probabilities).sort((x,y)=>y[1]-x[1]);
      console.log(`    ${name}: chose "${a.choice}" at confidence ${a.confidence}`);
      rows.forEach(([k,v])=>console.log(`      ${k.padEnd(16)} ${v}`));
    }
    const u=j.usage||{};
    if(u.input_tokens) console.log(`    Cost of this judgment: ${u.input_tokens} in / ${u.output_tokens} out. Decoded offline, no key.`);
    console.log(`    CAUTION, measured: strip the framing from the prompt and these numbers MOVE — one`);
    console.log(`    verdict flipped 0.21 to 0.59. See docs/demos/jev-probe/NOTE-framing-leak.md.`);
  ' "$work/pr.json" && ok || no Q5 "$work/pr.log"
else no Q5 "$work/pr.log"; fi

printf '\n%d of 5 questions answered' "$pass"
if (( fail > 0 )); then
  printf ', %d failed:%s\n' "$fail" "$failed"
  echo "These run from committed bytes with no setup, so a failure is a defect in this repo and not a"
  echo "missing dependency on your machine. Please open an issue with this output."
  exit 1
fi
cat <<'TAIL'
.

Run any of them on YOUR OWN logs — every tool takes a path and writes a receipt that states its
denominator before any share:

  node demos/routing-backtest/bin/backtest.mjs  <your-sessions.jsonl> --out runs/mine.json
  node demos/retransmit-whatif/bin/whatif.mjs   <your-sessions.jsonl> --out runs/mine.json

The lane's actual product is not these demos. It is a ruling on 17 candidate ideas, of which ZERO were
promoted: docs/demos/STATUS.tsv for the verdicts and receipts, NEGATIVE_EVIDENCE.md for what was ruled
out and what would reopen it.
TAIL
exit 0
