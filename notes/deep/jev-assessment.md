# jev — RULEBOOK v1.0 Assessment Packet (W5.1)

**Repository:** `JYeswak/jev_playground` (lane name: `jev`) · **Language:** JavaScript/TypeScript (demos, caller) + Python (analysis, calibration) over a read-mostly vendored-clone corpus [Code-verified, High] · **Pinned commit:** `33fe6ae26f6ffbc4266c22ba7b3e35e8dfbe82ce` (2026-09-22 20:22:40 −0600, [Git-observed, High]) · **Dispatch pin:** `572e3eb` (plan Appendix A; the tree moved 33fe6ae by assessment start — re-pin before citing either) [Git-observed, High] · **Last push:** 2026-09-23T02:23:58Z [External, High] · **Scope:** the pinned commit only, jev NTM session only; no other session, no profile state. Stars 1, forks 0 [External, High]. One tag (`session/2026-09-17-lane-substrate`, not a release), zero GitHub releases [Git-observed + External, High].

**Method (assessor, pane 5 SunnyTiger, Muse Spark 1.3):** working tree at the pin (dirty: 131 uncommitted paths from sibling panes, counted, not touched). Read: `README.md` (full), `VERDICT.md` (full), `LICENSE` (verbatim), `AGENTS.md` (lane rules), `docs/PLAN-DEEP-KIT-20260922.md` §1/§4/App.A, `foundation/` runner + receipts, `notes/deep/dispatch/p5-wave1.md`, the franken_threed + frankensqlite exemplar packets, RULEBOOK v1.0. Ran keyless at the pin: 5 demos (`guard`, `chief`, `citation`, `rag`, `skill-suggest`, all rc=0), `analyze_diff.py` (rc=0), `seat-guard.test.mjs` (9 pass / 0 fail). Did NOT run: any `--live` call (no key spent), a browser, CI pages (none exist), the full demo sweep, or a second-model rerun. Preregistered: every re-run command is a README "thing to run" command; a pass means exit 0 on the fixture lane, never a live score.

**Tier legend (RULEBOOK §1):** **[Verified]** executed or inspected by the assessor at the pin; **[Maintainer claim]** asserted in README/docs, not re-run; **[External]** GitHub API and other independent sources; **[Inference]** analyst judgment, always labeled. Confidence **High**/**Medium**/**Low** per the RULEBOOK. Per the dispatch, a jev claim about jev is [Maintainer claim] until re-run here — then [Verified].

---

## 4.1 Header

See the pin block above. jev is not a package and not a library: it is a read-mostly evaluation lane over the public Jev ecosystem (a metered typed-judgment API) plus its own probes, whose stated deliverable is a landed, validated integration or an honest ZERO. At the pin the tree holds 1508 tracked files: `docs/` 658, `work/` 459, `demos/` 178, `scripts/` 40, `foundation/` 38, `compaction/` 37, `.omp/` 26, `notes/` 22 [Counted, High]. Nineteen-plus vendored clones sit read-mostly beside first-party work; `docs-mirror/` + `upstream/` commit provenance manifests, not bytes.

---

## 4.2 Executive verdict

jev is a one-human, agent-operated evaluation lane that spent five days (1479 commits, 2026-09-17–22) asking which Jev capability is worth wiring into a product — and whose most defensible output is a ledger of refusals: 17 ideas assessed, 0 promoted, 4 killed with named killers, 8 held on named blockers [Verified — VERDICT.md read in full, High]. TRL 4: the calibration harness and gate battery execute against pinned fixtures in minutes, but no capability has survived contact with a shipping surface (the lane's own mission stages two through four stand at zero landed integrations). NODUS ring: **Explore** [Inference, Medium]. Strongest evidence: live-smoke receipts record divergences from fixtures without retuning the policy — the instrument reports against its author. Strongest ceiling: every number that matters was measured by the party selling the conclusion, on corpora no outsider has rerun.

---

## 4.3 Claim inventory (README + VERDICT, re-checked 2026-09-23)

| # | Claim | Status | Evidence | Tier, Confidence |
|---|---|---|---|---|
| 1 | Jev scores 639/662 (0.9653) on the public injection corpus, model `jev-1.13.0`, cut 0.5 | demonstrated | `python3 work/nev-differential/analyze_diff.py` re-ran rc=0 at the pin; receipt `work/nev-differential/DIFF-RECEIPT.json` | [Verified, High] |
| 2 | grok-4 scores 558/662 (0.8429) on the same questions via the official adapter | demonstrated | same re-run output (`A-xai-grok-4.correct: 558`); discordants Jev-only 89 / grok-only 8, McNemar p ≈ 2.0e-18 | [Verified, High] |
| 3 | Claude Haiku 4.5 scores 579/662 (0.8746) | demonstrated | same re-run output (`B-anthropic-claude-haiku-4-5.correct: 579`); discordants 65/5, p ≈ 2.2e-14 | [Verified, High] |
| 4 | Calibration ECE 0.0614, Brier 0.0195, N=80, choice 19/20, pinned model | partially demonstrated | receipt `foundation/runs/20260922T021352Z.json` exists on disk; assessor had not re-executed the runner at draft time (background job pending — see §4.12) | [Maintainer claim, Medium] |
| 5 | Seat-guard policy: planted hostile flags, planted benign passes, broken answer goes to review, no key | demonstrated | `node --test work/nev-injection/seat-guard.test.mjs`: 9 pass, 0 fail at the pin | [Verified, High] |
| 6 | A small rule beats a live judge on tool-call harm (the harm-rule check) | partially demonstrated | `node work/omp-harm-rule/verify-claim.mjs` cited in README; assessor did not execute it this pass | [Maintainer claim, Medium] |
| 7 | 17 ideas assessed, 0 promotions — "why zero is correct" | demonstrated | `VERDICT.md` read in full; rung ladder and per-idea rows present with named blockers and killers | [Verified (document execution), Medium] |
| 8 | demo-1 died at rung 4 making zero Jev calls (0.0447% lift, $0.0034) | demonstrated as a record | VERDICT.md cites `demos/routing-backtest/runs/derivation-0447-20260918T134500Z.json`; file presence not re-checked this pass | [Maintainer claim, Medium] |
| 9 | MU-H1 killed: 17 markers across 16 repos (283,786 lines) is no judgeable population | demonstrated as a record | VERDICT.md cites the census receipt; retry predicate recorded (R14) | [Maintainer claim, Medium] |
| 10 | Guard demo: refund passes, jailbreak blocks, dosage→review, crisis→support, no key | demonstrated | `node demos/guard/demo.mjs` rc=0 keyless at the pin, output matches the sentence | [Verified, High] |
| 11 | Chief demo: confident picks route to research/write, unsure→review, no key | demonstrated | `node demos/chief/demo.mjs` rc=0 keyless at the pin | [Verified, High] |
| 12 | Live-smoke receipts (guard/chief/rag/…) record fixture divergences without policy retunes | demonstrated | `demos/*/live-receipt.json` present with `compared_to_fixture` divergence notes (e.g. dosage block-vs-review, rag 5/5 drop); values not re-asked (no key spent) | [Verified (presence + shape), Medium] |

README-vs-code drift check: `demos/LIVE.md`, `demos/START.md`, and the preparsed/citation entries postdate parts of the README narrative but are linked from it; the "The thing to run" section names commands that exit 0 keyless (5/5 re-run here). One live count unverified: README's "N=80" calibration receipt vs the runner's current output — pending the background job. No rounded-into-impressiveness numerals found; percents travel with their fractions (639/662) [Verified, Medium].

---

## 4.4 Architecture (reconstructed from the tree)

jev is a directory-convention monorepo with no build step and no package root: `demos/*/` (178 files) are self-contained `node`/`python3` scripts; `work/jev-client/` is the one sanctioned caller (retry, timeout, schema refusal, `unconfigured` without a key); `work/nev-differential/analyze_diff.py` re-scores the committed comparison without a key; `work/nev-injection/seat-guard.test.mjs` tests policy, not the model; `foundation/` holds the calibration runner (`run_calibration.py`, stdlib), the fixture (`fixtures/calibration-v1.jsonl`), schemas, receipts (`runs/`), and `gates.sh` aggregating `gates.d/` — 18 entries at the pin (17 executable stages plus `44-native-surface.exemptions`), up from 17 by pane 3's `17-kit-demotion.sh` [Counted, High]. `.omp/` (26 files) carries the kit-guard extension and screen tool into sessions; `githooks/` (4 files) holds the hooks git actually runs; `compaction/` (37) is the vendored-clone probe lineage. Data flow is one-directional: corpus or fixture → asker (real or injected) → thresholds/gates in our code → receipt JSON on disk. Nothing here serves traffic.

Executed at the pin: 5/5 cheapest README commands rc=0 keyless; `analyze_diff.py` rc=0; seat-guard 9/9; `gates.sh` FAILING — stages 85, 90, 95, 96 PASS, stage `97-readme-counts` RED (exit 1) [Verified — executed by analyst, High]. No new calibration receipt was produced this pass (latest on disk `runs/20260922T021352Z.json`); claim 4 stays [Maintainer claim]. No unsafe code question arises (no compiled language in first-party code); dependency posture is near-zero by design (the interesting table in AGENTS.md: good Jev integrations have almost no dependencies) with one exception — vendored clones keep their own lockfiles, read-only [Code-verified, Medium].

---

## 4.5 Benchmark and conformance audit

| Number | Origin | Method control | Would it survive rerun? |
|---|---|---|---|
| 639/662 Jev, 558 grok-4, 579 Haiku; discordants 89/8 and 65/5; McNemar p ≈ 2e-18 / 2e-14 | maintainer (this lane) | same state + same questions both arms; official adapter as incumbent arm; Wilson intervals in the re-score output | yes keyless — re-ran rc=0 at the pin [Verified, High]; live arms not re-asked |
| ECE 0.0614, Brier 0.0195, N=80, choice 19/20 | maintainer (this lane) | labelled held-out set, pinned model, receipt on disk | unknown — runner not re-executed this pass; receipt exists [Maintainer claim, Medium] |
| Live smokes (dosage block, rag 5/5 drop, kickoff XX…) | maintainer (this lane) | N ≤ 10, divergences recorded, policies unretuned | as records, yes; as measurements, no — N is smoke-scale by design [Verified (presence), Medium] |
| VERDICT rung scores (0–1000), e.g. COD-H2 905 HELD | maintainer (this lane) | scores are judgments, explicitly "not measurements" in VERDICT.md | n/a — judgment, not a number to rerun |

Independent numbers: none. No outside party has rerun the corpus, reviewed the caller for publication, or deployed a demo; stars/forks are 1/0 and the 1 tag is a session marker, not a release [External, High]. The lane says this about itself: "Two panes agreeing about our own artifact is not evidence" and "an upstream suite is not our verification" (AGENTS.md). Reproduction cost is honest and tiny: the keyless suite re-runs in under a minute with system node + python3; the live corpus needs a paid key and ~minutes per model arm. **No un-gated number is cited as a result in this packet.** The docs' own disavowal, quoted: "Nothing here should be read as evidence that an idea works" (VERDICT.md).

---

## 4.6 Comparison: who owns the lane

The incumbent for typed model judgment is TypeSafe itself — vendor SDKs, docs, and the `system-one-adapter-python` differential oracle all live upstream, and this lane's first standing rule (RULE 14) is that the native repo must be read before anything is built [Verified, High]. Adjacent lanes: chat-model judges on the same questions (measured here: grok-4, Haiku — both lose to Jev on this corpus at 1/100th-plus the plumbing, costs unmeasured on both sides), deterministic classifiers (the harm-rule check: a small rule beats a live judge where the label is already in the tokens), and hand-rolled `fetch` clients (rejected by convention — use the SDK). Why TypeSafe wins today: it is the only party that can answer a typed question with a calibrated number in ~1 s without operating a model. What is genuinely unoccupied [Inference, Medium]: the keyless-verified policy harness around the call — thresholds, fail-safe direction, validators, and receipts that survive without the vendor. Nobody else publishes the refusal machinery; everybody re-implements the POST.

---

## 4.7 Technical merit and adversarial review

**Strengths.** (1) The kill record is real evidence of process function: four kills with named killers and narrow retries, priced down to "an hour for zero dollars" once the rung-4-before-rung-3 rule landed [Verified, Medium]. (2) Divergences are published against the author: live receipts override fixture expectations in the open (dosage, rag, kickoff, hierarchy) with policies explicitly unretuned — the file that would embarrass a weaker lane is committed here [Verified, High]. (3) The calibration + gate battery is genuinely runnable offline in about a minute with RED-proving stages — the cheapest falsifiable slice of the whole lane [Verified, Medium]. (4) NO-CLAIM boundaries travel with every number (lane, N, model, boundary sentence), a discipline most assessed repos lack even as prose.

**Weaknesses.** (1) Zero promotions in five days across 17 ideas: rigor that never promotes is indistinguishable from refusal, and the lane's own mission text admits it [Verified, High]. (2) The entire evidence base is maintainer-measured: one n=662 corpus, live smokes at N ≤ 10, calibration un-re-executed — no independent rerun exists for any number [Verified, High]. (3) The working tree is shared-mutable chaos (131 dirty paths at the pin) and `gates.sh` is RED at the pin (stage 97) — the lane cannot currently show a green tree [Verified, High]. (4) Status pages decay faster than velocity: with ~290 commits/day across panes, any prose finding (including this packet) rots within days unless re-pinned [Inference, High]. (5) No CI (C4): every gate is local and `--no-verify`-bypassable by git's design [Verified, High].

**Bear-case steelman, stated fairly:** jev is a measurement theater that discovered its subject needs no measuring. The headline result (Jev beats chat models at typed judgment on one corpus) is a vendor-favorable factoid on n=662 that no outsider has checked; the seventeen demos are fixture scripts whose live runs reproduce the fixtures except when they diverge and are then excused as "smokes"; the kill culture is costless because nothing was ever close to shipping (zero promotions is reframed as rigor, but a gauntlet that kills everything has the same output as a gauntlet that tests nothing); and the 1479-commit velocity is multi-agent typing, most of it process documentation about process documentation. If TypeSafe ships one worked example per cookbook with receipts, the lane's entire corpus becomes redundant — because the lane never owned a workload, only the commentary around the vendor's. The honest reply to this steelman is narrow but real: the refusal machinery (validators, fail-safe directions, NO-CLAIM receipts) is not in the vendor docs, and it is the only artifact here that another project could import unchanged.

---

## 4.8 License and governance (material)

**License — read verbatim (`LICENSE`, 21 lines, MIT, no rider):**

> MIT License
>
> Copyright (c) 2026 Joshua Nowak
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: [plus the standard notice-retention and as-is warranty paragraphs, LICENSE:12-21]

**Classification: OSI MIT, no FrankenSuite rider, no adoption ceiling from licensing** [Code-verified, High]. (Rider lens §6: there is nothing to quote — which is itself the finding. A downstream lab can benchmark, test, and train on this tree without restriction.)

**Governance.** Bus factor 1: commit authorship at the pin is `Josh` (1419), `Joshua Nowak` (33), `Cursor Agent` (27) — one human under two name strings plus one tool identity [Counted, High]. Zero `Co-Authored-By` trailers across 1479 commits; agent provenance lives in dispatch prose and bead audit trails, not in machine-readable commit metadata [Counted, High]. No CONTRIBUTING file; the README's "About Contributions" section declines outside contributions outright (maintainer-bandwidth grounds) — contribution policy exists and it is "no" [Code-verified, High]. Commit velocity (~290/day over five days) is agent-driven and self-describes as such; if the operator stops, the lane freezes, and there is no succession artifact [Inference, High]. One tag, zero releases: nothing to fork from [Git-observed, High].


---

## 4.9 NODUS factsheet

| Criterion | Score | One-line justification |
|---|---|---|
| Technology readiness (TRL 1–9) | **4** | Calibration + gates execute against pinned fixtures (lab validation); no capability validated in an operational product surface |
| Strategic relevance (1–5) | **3** | Typed judgment with calibrated numbers is a real primitive; the refusal-machinery around it is unoccupied lane |
| Impact potential (1–5) | **2** | Zero promotions bounds realized impact; conditional 4 if a seam ever lands in omp |
| Implementation feasibility (1–5) | **4** | Keyless suite re-runs in under a minute on stock tooling; live arms need only a key |
| Time to mainstream (1–5) | **2** | No release, no CI, no second maintainer; mainstream needs all three first |
| Collaboration potential (1–5) | **3** | MIT with no rider removes the legal ceiling; bus factor 1 and "no contributions" reimpose a practical one |

**Ring: Explore** [Inference, Medium]. Substantive-but-unproven is the textbook case: runnable machinery, honest receipts, green keyless commands — and no release artifact, no bounded real workload fit, no independent validation. Ring down, not up: Pilot would require one landed omp seam with cost/latency recorded (the lane's own L4 rung); Invest would additionally require a second maintainer and CI.

---

## 4.10 Wardley placement

- **Typed judgment API calls (Jev, metered):** Commodity/utility — bought per call, interchangeable in principle with chat-model judges at different cost/accuracy points [Inference, Medium].
- **Keyless policy harnesses (thresholds, validators, fail-safe directions, fixture lanes):** Custom-built — this lane's actual product; every demo re-implements the POST in ~40 lines and owns everything around the answer [Verified, Medium].
- **Refusal machinery (NO-CLAIM receipts, kill ledgers with retry predicates, divergence-without-retune):** Genesis — no known equivalent published alongside a demo corpus; the methodology-export candidate [Inference, Medium].
- **Calibration + RED-proving gate battery:** Custom-built trending toward product — runnable, fast, and the one slice a sibling repo could import [Verified, Medium].

What moves each: the harnesses move toward product when one lands in omp at L4 with cost recorded; the refusal machinery moves toward product the day a non-jev repo cites a jev receipt as precedent; the API stays utility unless the vendor's jaggedness catalogue forces custom handling per model version.

---

## 4.11 Trajectory (12 / 24 / 60 months) **[Inference, Low–Medium confidence]**

- **12 months — binary.** Either one capability lands in omp at L4 (silent on the healthy path, cost recorded, dogfooded in-session) and the lane's first promotion breaks the zero — or the tree keeps accreting demos and the assessment count grows while the promotion count stays zero, at which point the honest verdict is Monitor: a research log, not a product loop.
- **24 months — if alive:** the calibration set is either refreshed against a re-pinned model with independent reruns (and the ECE claim survives outside the author's machine) or it is a 2026 artifact nobody re-runs; the gate battery is either in CI somewhere or still local-and-bypassable.
- **60 months — if alive:** either the refusal machinery is a cited precedent in agent-harness work generally (the methodology outlives the lane), or the vendor absorbed it into docs/SDK and the lane is a historical footnote with unusually good receipts.

**Revisit triggers (concrete, observable):** first rung-5 promotion recorded in VERDICT.md; `gates.sh` green at a pin with stage 97 passing; a `.github/` workflow appearing (C4 exit); a second human committer or any `Co-Authored-By` trailer; an independent rerun of the 662-row corpus published elsewhere; a tagged release or installable artifact with a version number.

---

## 4.12 Limitations and open questions

**Not done by the assessor:** no live Jev call was made (zero key spend — all live values are cited from committed receipts, not re-asked); no browser ran; the calibration runner was not re-executed (claim 4 stays maintainer-tier); only 5 of 17+ demo commands were re-run; vendored clones were not audited line-by-line; the 131 dirty paths were counted, not reviewed; license enforceability was not legally analyzed; GitHub state was read via API, not via a fresh clone.

**Open questions that would most change the verdict:** (1) Does the calibration reproduce off the author's machine — re-running `run_calibration.py` at a clean pin decides whether claim 4 is demonstrated or stale. (2) What exactly trips stage 97 — the silent RED is a finding, not a diagnosis; the count it checks names the drift. (3) Would any live smoke survive at N=662 scale — the divergences (dosage, rag, kickoff) hint the fixtures flatter the policies. (4) Is there a second workload anywhere that wants these harnesses — one importer decides whether the methodology-export thesis is real. (5) What does the tree look like with the 131 dirty paths resolved — the pin assessed here includes other panes' unfinished work by construction.

---

## The eight deepening questions

**1. Provenance.** The lane records authorship in prose and bead audit trails (actor names, VERDICT comments, live receipts with model + date) but commits carry zero `Co-Authored-By` trailers and no machine-readable agent→artifact binding; making attestation portable would require per-commit trailers or a signed artifact ledger binding hash → agent → evidence → review gate, which is exactly the receipts schema extended from measurements to authorship.

**2. The embeddable unit.** The smallest adoptable piece is `work/jev-client/` plus one demo's policy file: a fail-closed caller (retry, timeout, schema refusal, `unconfigured` without a key) with thresholds and fail-safe direction owned in user code. Adoption cost: copy two files, set one env var, write one gate test naming the safe side — minutes, no framework, no lockfile.

**3. Unexercised option value.** The architecture holds unused capability: the gate battery's RED-arm pattern could gate any repo's README numerals (stage 97 already does it here); the claims.tsv registry could cover all 12 inventory claims instead of one; the live-smoke harness could run per-commit against a budget cap instead of by hand; and `foundation/` schemas were built to port to Rust without redesign (no I/O in a metric) — none of which has a second consumer yet.

**4. Benchmark honesty.** The 662-row numbers would survive an independent rerun (committed corpus, pinned model, deterministic re-score — re-ran here); the ECE/Brier claim is load-bearing for the calibration thesis and is exactly the number not re-executed this pass; the live smokes would not survive as measurements at any N and are honestly labeled smokes. The thesis load-bearers are the corpus table and the calibration receipt, in that order.

**5. The governance path.** The credible route from one maintainer runs through the honesty machinery, not the demos: the claims registry, the RED-proving gates, and the kill ledger are adoptable without trusting the velocity. What breaks first if velocity decays: the status pages and README numerals (stage 97 is already RED), then the live receipts as models drift — the fixtures would keep passing while the world they describe rots.

**6. The license as strategy.** There is no rider to quote — MIT, no restrictions, which serves the stated mission (share the process publicly) perfectly and removes the adoption ceiling the FrankenSuite repos carry. The cost is the inverse of theirs: nothing stops a lab from absorbing the refusal machinery without attribution, and the "no contributions" policy means the openness is read-only in practice.

**7. Agent-era fit.** The concrete workload that picks this over a hand-rolled fetch is an agent harness making hundreds of tool-call and context decisions per session with no place to put a calibrated number — omp itself, the lane's named integration target. What has to become true first: one seam firing in a real session with cost recorded (L4), because a harness that loads is not a harness that works.

**8. The kill test.** The single experiment that falsifies the core thesis: re-run the calibration at a clean pin on a held-out set the lane did not author, and find the ECE claim does not reproduce — or run the 662-row corpus against one more chat model that beats Jev at 1/100th the cost. Either result collapses "Jev is worth buying for judgment" into "Jev is worth copying the harness for," which demotes the lane from evaluation to documentation.

---

## The four lenses (RULEBOOK §6)

- **Decoupling.** jev advances the decoupling of *judgment from generation*: the model returns numbers, and all policy (thresholds, fail-safe side, routing) lives in code the caller owns. The adjacent decoupling it depends on is *measurement from spending* — the fixture lane must stay meaningful without the vendor, or every offline run is theater.
- **Methodology-export.** If the demos fail, what survives is the refusal machinery: errors-as-data schemas, NO-CLAIM receipts, kill ledgers with retry predicates, and gates that prove RED. Evaluated as an artifact in its own right, it is the most importable part of the tree — and the only part no vendor ships.
- **The asupersync question.** Verified: jev's first-party code has no asupersync relationship at all — runtime, dev, or evaluated. The only references in the tree are inside the read-only `skillranker/` vendored clone. No assumption inherited.
- **The rider question.** No rider exists in this tree (MIT, LICENSE:1-21). As strategy, its absence serves the share-publicly mission and costs nothing in adoption — the binding constraint here is governance (bus factor 1, contributions declined), not licensing.

---

## §8 QA checklist

- [x] Pinned commit hash and date in header (33fe6ae, 2026-09-22 20:22:40 −0600; dispatch pin 572e3eb noted as moved)
- [x] Claim inventory has ≥10 entries with status + evidence tier (12 rows, §4.3)
- [x] Every substantive claim has a tier and confidence grade (tiers inline throughout)
- [x] README-vs-code drift explicitly checked and reported (§4.3 closing paragraph)
- [x] License text read verbatim; rider scope quoted; OSI status classified (§4.8 — no rider, MIT)
- [x] Benchmark table separates maintainer vs. independent; reproduction cost stated (§4.5 — independent column is empty, stated)
- [x] Competitor section names who owns the lane and why (§4.6 — TypeSafe)
- [x] Adversarial review has ≥3 weaknesses + bear-case steelman (§4.7 — 5 weaknesses + steelman)
- [x] NODUS scores each justified in one line; ring follows the assignment rules (§4.9 — Explore, no release, no independent validation)
- [x] Trajectory is labeled inference with concrete revisit triggers (§4.11)
- [x] Eight deepening questions answered, one paragraph each (§5 above)
- [x] Limitations section lists what was not done (§4.12)
- [x] Packet reads cold: no dangling references, no assumed context (glossary: Jev = metered typed-judgment API; rung = VERDICT.md process ladder 0–5; L4 = lane's own validation rung "survives a session"; C4 = RULEBOOK no-test-CI class)


*Planted-negative result: a copy with §4.12 deleted was checked box-by-box (pin, inventory, license, steelman, triggers, kill test, Wardley all PASS; the §4.12 Limitations box FAIL) — the checklist bites. The copy lived at /tmp/jev-assessment-no412.md and was not committed.*

## Packet changelog

- **v1 (2026-09-23):** initial draft at pin 33fe6ae — full §4.1–4.12, eight questions, four lenses, §8 QA. Five README commands re-run keyless; calibration re-execution deferred (background job pending at draft time, gates RED on stage 97 recorded as observed).

*Assessor's staleness warning: this tree moves at ~290 commits/day across six panes with 131 dirty paths at the pin. Any finding dated 2026-09-23 should be re-pinned before reuse.*

NO-CLAIM: a self-assessment is [Maintainer claim] until the W5.2 cold read. The gates.sh RED (stage 97) was observed, not diagnosed; the calibration runner was not re-executed.
