# Docs and upstream manifests refreshed against live upstream, with a citation check (bead `jev-j5fo`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. No Jev call; `scripts/sync-docs.sh` at
`72659d3` (idempotent since `jev-tssx`), run once in the main worktree at 04:15Z.

## What changed

**Pins: none moved.** The HEAD of every clone under `upstream/*/*` and of `$HOME/Developer/ripwire` was
recorded before and after the run, and the two lists are byte-identical (23 clones plus ripwire).
Every `pinned_sha` in `upstream/MANIFEST.tsv` is unchanged.

**`upstream/MANIFEST.tsv`**
- `system-one-adapter-python` stays pinned at `adffc2e`; upstream is now `e1d4cc9`, 1 behind.
- `ripwire` stays pinned at `f45087a7`; upstream is now `60b65f02`, 479 behind. Moving either pin is
  a Rule 14 item-4 decision and is not made here.
- The committed file carried a second `system-one-adapter-python` row, the conflicting duplicate
  `jev-goa` removed from the script. The refresh drops it: 24 lines become 23, with the same repos.

**`upstream/ORG-INVENTORY.tsv`:** new `pushed_at` for `system-one-adapter-python` (2026-09-22) and
`typesafe-sdk-python` (2026-09-21).

**`docs-mirror/MANIFEST.tsv`:** 114 rows, as before.
- 43 pages changed content.
- 4 Python SDK client pages left the site: `sdk/python/api/clients/{async,sync}/{client,models}.md`.
- 4 pages arrived: `cookbooks.md`, `introduction/coding-agents.md`,
  `sdk/python/api/clients/{async,sync}.md`.
- `llms.txt` still lists 111 pages, and `sitemap.xml` still has 111 `<loc>`. `llms-full.txt` grew
  from 835,504 to 910,292 bytes.
- The old copies of the 4 removed pages stay on disk in this worktree; the script does not delete, and
  they are gitignored. A fresh clone does not have them.

## Citations of changed pages

I searched README.md, AGENTS.md, docs/demos/**, work/** and foundation/kit/claims.tsv for
`docs-mirror/typesafe/<page>` and `docs.typesafe.ai/<page>`, with or without `:line`. That found 60
citations of 28 changed pages. 8 of them sit inside the tool-result sample JSON, which quotes old agent
output and is not a claim. No removed or added page is cited. The pre-refresh mirror was
snapshotted to `/tmp/claimcheck-mirror-before/` and each cited passage was read old against new.

**The two named first: both still hold.**
- **`models.md` pricing.** Line 13 still reads `| Price (per Btok / per Mtok) | \$42 / \$0.042 |` for
  `jev-1.13.0`. The page gained "Context length" and "Input" rows and four sections (customizing,
  language, data handling). **The "Output tokens are free" bullet moved from line 16 to line 18.**
- **`primitives/choice.md` 255-option limit.** Line 355 is byte-identical: "A Choice question accepts
  up to 255 options". Line 388 (`other: 'A return reason that fits none of the above'`) is also
  unchanged. The page's changes are in its worked example: a new `returns` option text, response
  numbers, and `jev-latest` becoming `jev-1.13.0`.

**Citations that broke or went stale.** Each was reported to its owner; none was edited here.

| Citation | What it says | Now | Owner told |
|---|---|---|---|
| `work/jev-billing-units/measure.mjs:94` (`jevOutputFree`, `line: 16`) | the output-free sentence is at `models.md:16` | at `:18`. **The keyless re-score now exits 1**: "price source moved" | BillingUnits |
| `docs/demos/upstream-repro/jev-billing-units-20260924.md:12` | `api.md:183-191` lists `usage` `input_tokens`/`output_tokens` | still listed, now at `:198-206` | BillingUnits |
| `AGENTS.md:106` | `models.md:13,16` for "input only, output free" | `:13` holds; the output-free sentence is `:18` | Main |
| `docs/demos/duel-2/RUNG4_LABEL_PLAN_MU.md:71` | `models.md:13-16`, "input only, output free" | price holds at `:13`; output-free is now outside the range, at `:18` | Main |
| `docs/demos/upstream-repro/jev-curate-w70-20260923.md:164,165,171` | `score.md:272`, `score.md:299`, `noul.md:254` | same statements, now at `score.md:564` ("Should have at least two levels; the API accepts up to 10"), `:591`, `noul.md:248` | Main |
| `docs/demos/upstream-repro/choice-banking77-20260924.md:67` | "Jev's formula is not published (`confidence.md`)" | **stale.** `confidence.md` now embeds a widget whose Choice confidence is `(k·p_max − 1)/(k − 1)`, the adapter's formula. On committed rows (banking77 runs 2 and 3, clinc150 run 2; 1,550 Choice answers) it matches Jev's returned `confidence` within 0.02 on all of them and within 0.011 on 1,470. [INFERENCE] The gap is rounding, since probabilities are returned to 2 decimals. | ChoiceBanking77 |
| `AGENTS.md:779` | `llms-full.txt` is "one 835 KB text file" | 910 KB | Main |

**Citations that still hold.**
- `models.md:13` and `:13-16` for the price: `PLAN.md:3082`, `QUEUE.md:570`,
  `jev-billing-units-20260924.md:19`, `measure.mjs:92`.
- `choice.md:355`/`:388` (4 citations). `consistency_choice_cookbook.md:90`, the Haiku list price
  `"claude-haiku-4-5": (1.00, 5.00)`.
- `confidence.md` "never locked into our definition" (`jev-benchmark-pairing-20260918.md:71`).
- The three `patterns/*` pages, whose changes are additions only.
- `llms.txt` "111 pages" and `sitemap.xml` "111 `<loc>`".
- The 18 cookbook links in the README demo table. Their changes are summary wording, diagram styling,
  the install line (`typesafe-sdk ... --extra-index-url` becomes `cooksafe>=0.2.0,<0.3.0`),
  playground links, a helper rename, and in `sde_cascade` a dated price note. None changes a
  threshold, a question or a result that a demo row states.
- `citation_check.md`'s question wording is unchanged; only its summary sentence dropped "its
  confidence can flag the citation for human review". So `work/noul-scifact/run.py:40` holds.
- `llm_guardrails.md` changed only its summary (`noul-toxicity-20260924.md:7` holds).

**Gates after the refresh:** stage 15 PASS (41/75), stage 95 PASS, stage 97 PASS, and `readme-gate
--profile workspace README.md` exit 0. No README or claims.tsv citation broke, so nothing went to
ReadmeStrangerRun.

**NO-CLAIM.** The search found path citations, not paraphrases of a page. One snapshot of
docs.typesafe.ai at 04:15Z. The confidence-formula match is on committed rows, descriptive, with no
new call.

## After `6982002` (Main's FETCH_HEAD fix), re-checked 2026-09-24 07:43Z

The refresh at `4f3e295` ran with the script from before `6982002`. That script read `upstream_sha`
from FETCH_HEAD's first line, which after a full fetch on a detached pin can be any branch.

**The refreshed rows were not affected.** In the main worktree, FETCH_HEAD's first line equals the
default branch's line for every row that moved or that `6982002` names:

| Repo | Default branch | Line 1 | Default branch's line |
|---|---|---|---|
| system-one-adapter-python | origin/main | e1d4cc9 | e1d4cc9 |
| typesafe-sdk-js | origin/main | 66880cc | 66880cc |
| typesafe-sdk-python | origin/main | 0ffd094 | 0ffd094 |
| ripwire | origin/main | 60b65f0 | 60b65f0 |

**A stranger's fresh clone, `[oracle]`.** `git clone` of `c99310d` into `/tmp/claimcheck-verify-tssx`,
which contains both `4f3e295` and `6982002`:
- Sync run 1: rc 0, `git status` 0 lines.
- Sync run 2, with typesafe-sdk-js FETCH_HEAD line 1 now `codex/npm-bootstrap` (0098f35), the trap
  state: rc 0, `git status` 0 lines. The row stays `66880cc/66880cc/0`. `--check` PASS 114/23.
- The pre-`6982002` script as run 3 rewrites that row to `66880cc/0098f35/1`, so the fix is what
  holds the tree clean.

An earlier single-sync stranger check, at `d20ba4e` before `6982002`, was also clean, but run 1
alone never reaches the trap.
