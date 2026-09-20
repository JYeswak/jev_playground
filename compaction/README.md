# omp-compact-replay

Offline replay harness: omp session transcripts through `fast-jev-compaction`,
verifying the library contract on omp-shaped traffic.

## Layout

- `src/omp-adapter.ts` — `omp -p --mode json` event stream → `Message[]`.
  Reads `message_end` rows only (streaming `message_update` partials ignored).
  Assistant `thinking` blocks are dropped and counted (the library has no
  thinking channel; carrying them as text would corrupt its verbatim contract).
  Standalone `toolResult` messages attach to the message immediately FOLLOWING
  the call's message (any role; the library pairs by id, role-free).
  Call-adjacent placement keeps each result in its call's own pin window.
  A result whose call is in the final message lands on one trailing empty user
  message and is counted — never silently dropped.
- `test/adapter.test.ts` — deterministic mapping tests + known-bad
  (trailing result must be kept).
- `fixtures/` — real captured transcripts. `omp-session-20260917.jsonl` is a
  6-call session (fits the pin window; adapter-only proof). The `-big-`
  capture has 11 tool calls so middle calls become Jev candidates.
- `runs/` — live replay receipts (manual, like calibration runs).

## Use

```sh
npm install
npm test                      # 38/38, re-verified 2026-09-20
npm run replay -- <t.jsonl> [--out runs/r.json]   # NEEDS TYPESAFE_API_KEY; exits 2 without one
#   keyed, from a fresh clone: fixtures/omp-session-big-20260917.jsonl -> 13 messages to 8,
#   1 request, 1439 ms, 6/6 invariant checks PASS. The small fixture makes 0 requests: it has
#   no compaction candidates, so a green run there proves the harness, not the compaction.
../../foundation/gates.d/40-omp-compact-replay.sh   # gate (hermetic)
```

## Resume-quality A/B boundary

`ab/run-ab.ts` records arm scores and sampling evidence. It does **not** emit a
relative verdict for the historical single-sample runs: an arm is only eligible
for a requested verdict after at least 10 zero-spread samples. The three existing
receipts retain their observed scores but mark their old n=1 verdicts retracted;
the identical fixture producing arm-B scores 1 and 3 is evidence of variance, not
a result. `ab/verdict.ts` and `test/ab-verdict.test.ts` cover the red arm and the
minimum sample contract.

- Thinking content is dropped (counted in receipt). If a future task needs
  reasoning preserved, the adapter must grow a channel for it — currently none.
- Single-turn `-p` sessions put every result after the only user turn; the
  call-adjacent rule still places each result next to its call.
- The `-big-` fixture keeps full raw rows including opaque `thinkingSignature`
  blobs (provider metadata, never model content).

## Installing the omp compaction hook

This turns the compactor into something omp calls for you: when a session hits its context limit,
omp asks this hook first, and the hook either returns a smaller transcript or declines and lets
omp's own summarizer run.

**It cannot break your session.** Every failure path — no API key, Jev unreachable, a malformed
envelope, output that did not actually shrink — returns `undefined`, which means "omp, you do it".
That was not a design claim until 2026-09-19, when the hook was wrong four times in a row against
a real omp and no session was harmed. See `../docs/demos/omp-seam-live-20260918.md`.

**Into any repo, which is the path you want.** From a fresh clone of *this* repo you need the
compactor first — it is not vendored here, and the installer prints these exact lines if it is
missing:

```bash
git clone https://github.com/tamaratran/fast-jev-compaction fast-jev-compaction
(cd fast-jev-compaction && npm install && npm run build)
```

**The build is not optional.** The package exports `./dist/index.js`, which npm publishes but git
does not carry, so a bare clone resolves to nothing and the installer aborts. This exact sequence
— clone, build, install — was run end to end from a fresh clone of this repository on
2026-09-19 and ended `PASS`, rc=0.

It is cloned to the **repo root**, not under `upstream/` — the installer reads
`$repo/fast-jev-compaction`. An earlier version of this page said `upstream/tamaratran/`, which
was wrong: following it exactly still failed, verified from a clean clone.

Then:

```bash
./compaction/install-jev-compact.sh /path/to/your/repo
```

It copies the hook, vendors the compactor and its dependency under
`<target>/.omp/lib/jev-compact/`, drops a `SKILL.md`, writes an `INSTALL-RECEIPT.txt` pinning the
`fast-jev-compaction` version and sha, and refuses loudly rather than half-installing. Verified on
2026-09-19 against a scratch target: `PASS: jev-compact installed (placement + dependency; firing
proven only by /compact + log)`.

Then, in the target:

```bash
export TYPESAFE_API_KEY=...   # or launch under your secret manager.
                              # WITHOUT A KEY THE HOOK REGISTERS NOTHING AND OMP IS UNAFFECTED.
omp -p 'reply OK'             # a throwaway session, not one you care about
```

The installer's own closing line is the honest bar, and it is worth repeating: **placement is not
firing.** It proves the files are where omp looks and the dependency resolves. Whether the hook
ever runs is answered only by `/compact` and the log below.

### Did it actually do anything?

omp can swallow hook stderr, so a working hook and a dead one look identical from outside. The hook
therefore appends every decision to `~/.jev-compact.log`:

```
$ tail -2 ~/.jev-compact.log
2026-09-19T01:26:51.059Z passthrough: below minimum reduction: 0% reduction; no tool calls
2026-09-19T01:23:06.489Z refused: no messages on the event envelope; envelope keys: ...
```

`compacted A -> B` means it shrank the transcript. `passthrough:` and `refused:` both mean omp's
summarizer handled that compaction and nothing was lost. Set `JEV_COMPACT_LOG` to move the file.

### What the installer has actually been run against

Three re-install defects were found and fixed on 2026-09-19 by exercising these paths rather than
reading the script, so the list is evidence, not reassurance:

| case | behaviour |
|---|---|
| fresh empty target | installs; 1 skill file, no nested directories |
| re-install, nothing changed | idempotent, **zero** notes, no backup churn |
| you edited the hook entry | **backed up** to `jev-compact.ts.superseded-<UTC>`, announced |
| you edited a vendored source | same: backed up and announced |
| you edited `SKILL.md` | same — and re-install now *refreshes* it, which it previously never did |
| a sibling hook of your own | untouched |
| read-only target | fails closed: `RED: cannot create dirs`, **nothing created** |
| **installed hook actually fires** | **yes — proven outside this repo**, see below |
| **whole chain from a fresh clone** | clone → build → install → **fires**, end to end, rc=0 |

The last row is the one that matters, because every earlier version of this section could only
claim *placement*. Installed into a scratch target, then omp run **from that directory** with a
key and a prompt large enough to trigger compaction:

```
2026-09-19T08:20:33Z passthrough: below minimum reduction: 0% reduction; no tool calls
```

The hook loaded from a foreign repo, resolved its vendored dependency, was handed a real
compaction event, and returned a reasoned decision. `passthrough` is the correct answer there —
a single huge prose turn has no tool results to drop — and it is a *decision*, not a failure to
load. Placement is no longer the boundary; what remains unproven is a measured **reduction**,
which needs a session whose older prefix contains tool calls.

**Not tested:** a symlinked `.omp`, two installs running at once, and a target whose `node_modules`
you have modified (it is replaced wholesale, without comparison). Backups are copies, not merges —
you reapply your change by hand.

### How much does it actually save? Measured on six real sessions

Not on fixtures — on transcripts omp wrote during real work on this machine, replayed through the
harness with a real key. All six passed all six invariant checks.

| session | tool calls | requests | chars before → after | saved |
|---|---|---|---|---|
| a small one | 10 | **0** | 44,819 → 44,819 | **0%** |
| `UdsFeatureUnion` | 9 | 1 | 155,837 → 104,443 | 32% |
| `MirrorAgentsSurvey` | 15 | 1 | 249,949 → 188,661 | 24% |
| `OmpExtensibility` | 15 | **0** | 253,465 → 253,465 | **0%** |
| `PortFleetComposite` | 108 | 1 | 501,502 → 6,084 | **98%** |
| `PortOmpIdleDispatch` | 98 | 1 | 291,909 → 12,911 | **95%** |

**The two long sessions collapse to a few kilobytes in one request.** The two zeroes are not
failures and not noise: everything in them was *pinned*, so there was nothing the hook was allowed
to touch, and it correctly spent nothing finding that out.

**The predictor is LENGTH, not tool-heaviness.** A tool call is pinned when its call *or* its
result sits in the last six messages, so a transcript of seven to nine messages has almost nothing
outside the protected window no matter how many tools it used — `OmpExtensibility` above has
**15 calls in 7 messages and all 15 are pinned**. Long sessions expose nearly all of theirs: 108
calls, 5 pinned.

Across every real session on the machine this was measured on — 1,653 of them, at the library's
default settings:

| | sessions |
|---|---|
| at least one call the hook could ask about | **1,415 (86%)** |
| everything pinned, nothing to touch | **98 (6%)** |
| too large for Jev's state budget | **87 (5%)** |

**Do not read 98% as a rate.** Six sessions, one machine, one person's workload, and a third of
them saved nothing.

Reproduce on your own sessions — no fixture, no setup beyond the install above:

```bash
npm run replay -- ~/.omp/**/agent/sessions/**/<a real session>.jsonl
```

### Known limits, so you are not surprised

- **Savings come from tool results and thinking blocks.** A session that is one long prose turn has
  nothing this can remove, and it will correctly decline with `0% reduction; no tool calls`.
- It only ever sees `preparation.messagesToSummarize` — the older prefix omp has already decided to
  summarize. Recent turns are omp's to keep, and this hook does not touch them.
- Tested against omp 18.2.4. The envelope shape was discovered by observation, not documentation,
  so a different omp version may present something else; the hook refuses loudly in the log rather
  than guessing.
