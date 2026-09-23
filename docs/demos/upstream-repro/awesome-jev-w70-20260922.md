# awesome-jev W7.0 receipt — 2026-09-22

Class: catalogue. Tests run: T1, T3. T10 is the verdict, not a measurement arm. No live Jev call. Clone not edited. No repos cloned. `EVAL.md` not edited.

Re-run (non-author, read-only, no network):

```bash
env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR python3 - << 'PY'
import os, re, subprocess
from pathlib import Path
root = Path("/Users/josh/Developer/jev")
clone = root / "awesome-jev"
sha = subprocess.check_output(["git","-C",str(clone),"rev-parse","HEAD"], text=True).strip()
status = subprocess.check_output(["git","-C",str(clone),"status","--porcelain=v1","-uall"], text=True)
assert sha == "ef193004eba48e83339a6e7498e70530badd23a5", sha
assert status == "", status
text = (clone / "README.md").read_text()
pat = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
pins = re.findall(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:commit|tree|blob)/[0-9a-fA-F]{7,40}", text)
repos = {f"{m.group(1)}/{m.group(2)}".lower() for m in pat.finditer(text)}
assert not pins, pins
assert len(repos) == 71, len(repos)
print("PASS", sha, "repos", len(repos), "commit_pins", 0, "status_clean", True)
PY
```

Expected first line: `PASS ef193004eba48e83339a6e7498e70530badd23a5 repos 71 commit_pins 0 status_clean True`

## T1 — pin and environment

| field | value |
|---|---|
| full SHA | `ef193004eba48e83339a6e7498e70530badd23a5` (`git rev-parse HEAD`; prefix `ef193004eba4` matches the assignment) |
| `origin/main` | same SHA (`git rev-parse origin/main`). Local tracking ref only; no fetch |
| commit date | `2026-09-17T23:43:20+08:00` (`git log -1 --format=%cI`), author AnotiaWang, subject `收录近期社区 GitHub 项目，并补两则有意思的 demo` |
| observation clock | `2026-09-23T03:16:09Z` (`date -u` on `Joshs-Mac-Studio.local`); local `2026-09-22T21:18:21-0600` |
| license | CC0 1.0 Universal, `awesome-jev/LICENSE:1` (7105 bytes). README points at it at `README.md:225` |
| git status before | empty (`git status --porcelain=v1 -uall` at 03:16:09Z) |
| git status after investigation | empty (same command, exit 0, SHA unchanged). Receipt path is outside the clone |
| branch | `## main...origin/main`, remote `https://github.com/AnotiaWang/awesome-jev` |
| parent gitlink | `git -C /Users/josh/Developer/jev ls-files -s awesome-jev` printed nothing. Cleanliness is the clone's own status, not a parent index entry |
| tree | `.gitignore`, `CONTRIBUTING.md`, `LICENSE`, `README.md`, `README_zh.md` (`git ls-tree -r --name-only HEAD`) |
| `OMP_PROFILE` | unset (after `unset`, and `env -u` before `omp --version`) |
| `PI_PROFILE` | unset |
| `PI_CODING_AGENT_DIR` | unset |
| other `OMP_*` / `PI_*` | none set |
| runtimes | `omp/18.2.10` (env unset; clone does not invoke omp). `git version 2.50.1 (Apple Git-155)`. `Python 3.9.6` used for the census only. `node v22.22.0` unused. Host `Darwin arm64`, macOS 26.5.2 (`25F84`) |
| worker | `W70Awesome` on `Joshs-Mac-Studio.local` |

**T1: PASS.** Full SHA, both dates, license, and clean status before and after are recorded. Profile variables were unset. The clone has no language runtime of its own.

## T3 — claim inventory and entry pins

Method, two routes, both local:

1. Regex over `awesome-jev/README.md` for `https://github.com/<owner>/<repo>` and for `/commit|tree|blob/<hex>`.
2. `git remote get-url origin` plus `git rev-parse HEAD` on every directory under `/Users/josh/Developer/jev` and `upstream/` that contains `.git` (46 clones). Match key is `owner/repo`, case-insensitive. A third check: the same regex on `README_zh.md` yields the same 71 keys (`EN_ONLY` empty, `ZH_ONLY` empty).

Census: **71** unique GitHub repos. **0** commit, tree, or blob pins. `CONTRIBUTING.md:29-32` is why: the required link shape is `https://github.com/org/repo` with no SHA slot. Zero pins is the format, not a missed scrape.

"Named at a SHA" below means the catalogue URL contains a commit SHA. It does not, for any of the 71. A workspace clone at some other SHA is not that SHA.

### Five-plus entries

| # | entry | claim | catalogue SHA | that SHA in this workspace | status | deciding file:line | RULEBOOK tier |
|---|---|---|---|---|---|---|---|
| 1 | What is Jev | Choice returns `choice`, `probabilities`, `confidence`; Score returns `score`, `probabilities`, `confidence`; Noul returns `noul` in 0–1 (`README.md:32-34`) | none (no repo) | no catalogue SHA | **partial** | schema matches at `upstream/typesafe-ai/typesafe-sdk-python` `0ffd094c72ed`, which the catalogue did not name: `src/typesafe_sdk/_schemas/models.py:13,19,25` (choice, confidence, probabilities), `:109,115,127` (score, confidence, probabilities), `:75-77` (noul, "from 0 to 1"). No live response was requested | [Verified] schema field names only. Not a served answer |
| 2 | `AbdelStark/s1-rs` | "Rust derive layer for Choice / Score / Noul, typed question sets, confidence gates, and network-free tests" (`README.md:76`) | none. URL `https://github.com/AbdelStark/s1-rs` | no catalogue SHA. Workspace clone exists at a different, unnamed pin: `s1-rs` and `upstream/AbdelStark/s1-rs` both `b9168979a9be` (12-hex prefix `b9168979a9be`) | **partial** | mechanism is in that unnamed pin: `s1-rs/crates/s1-derive/src/lib.rs:26,34,50` (`derive(Choice/Score/Questions)`); `s1-rs/README.md:52` (network-free `FakeClient`); `s1-rs/README.md:152-155` (`NoulPolicy` gate). Not re-tested this run | [Verified] source presence at an unnamed SHA. Not a catalogue pin |
| 3 | `browser-use/jev-ultrafast` | Jev picks operation and DOM element; small LLM writes text only for `TYPE_TEXT`; Zürich → London in ~7s (`README.md:89`) | none. URL `https://github.com/browser-use/jev-ultrafast` | no catalogue SHA. Workspace pin `452c1ad2dd62` at `jev-ultrafast` and `upstream/browser-use/jev-ultrafast` | **partial** | clone headline is 7.1 seconds (`jev-ultrafast/README.md:9`); recorded completion 7.073 s (`jev-ultrafast/docs/performance.md:28`). Catalogue rounds and drops the clone's own limit: six runs, median 7.092 s, "not a general reliability benchmark" (`jev-ultrafast/README.md:118`). Flight not re-run | [Maintainer claim] of the ultrafast README, inspected, not re-executed |
| 4 | `anisselbd/jev-phishing-bench` | "2,000 emails: Jev vs Claude Haiku 4.5 on click-or-not … Haiku wins accuracy here" (`README.md:164`) | none. URL `https://github.com/anisselbd/jev-phishing-bench` | no catalogue SHA. Workspace pin `1d56e8c64d02` at `jev-phishing-bench` and `upstream/anisselbd/jev-phishing-bench` | **partial** | clone headline table: Jev 62.6% [60.5, 64.7], Haiku 81.3% [79.5, 82.9] (`jev-phishing-bench/README.md:11-13`). `results/metrics.json:3` `n_emails` 2000; `:196` accuracy 0.626; `:1396` accuracy 0.813. Not recomputed from raw rows. Same README `:49-54` says the five-signal regression gap is not a significant Haiku win (McNemar p = 0.063). Blurb covers click-or-not only | [Maintainer claim] of the bench files, file-present, not recomputed |
| 5 | `bitnovus/jev-spam-eval` | "Exploratory zero-shot spam study vs trained TF-IDF baselines, with post-hoc-tuning caveats" (`README.md:163`) | none. URL `https://github.com/bitnovus/jev-spam-eval` | no catalogue SHA. Workspace pin `76ef18305710` at `jev-spam-eval` and `upstream/bitnovus/jev-spam-eval` | **partial** | caveats are in the clone, not in the blurb: detailed criteria written after reading mistakes in 1,000 sampled emails; plain question 96.0% (`jev-spam-eval/README.md:22-26`). TF-IDF comparison is the README's subject (`:6-8`). Not re-run | [Maintainer claim] of the spam-eval README, inspected |
| 6 | `y0usaf/pi-jev` | "Pi extension with a shadow-mode tool-call gate, output judge, and typed `jev_ask`" (`README.md:145`) | none. URL `https://github.com/y0usaf/pi-jev` | no. Repo absent from the 46-clone origin census | **aspirational** | deciding lines are the catalogue line itself (link has no `/commit/`) and the absence census. Not opened | [Maintainer claim] of the list only. Unchecked |
| 7 | `jomatsu/pi-jev-auto-mode` | "Jev semantically approves `bash` / `write` / `edit`, and fails closed when it cannot decide" (`README.md:147`) | none. URL `https://github.com/jomatsu/pi-jev-auto-mode` | no. Absent from the origin census | **aspirational** | `README.md:147` plus absence census. Not opened | [Maintainer claim] of the list only. Unchecked |
| 8 | `teyhouse/jev-secret-detection` | "Secret-in-diff detector with repeatable Jev verdicts" (`README.md:108`) | none. URL `https://github.com/teyhouse/jev-secret-detection` | no. Absent from the origin census | **aspirational** | `README.md:108` plus absence census. Not opened | [Maintainer claim] of the list only. Unchecked |

No claim in this table is **demonstrated** as a live Jev behavior, **disproven**, or **stale**. Partial means the sentence matches a file at a workspace SHA the catalogue did not name, or matches a schema, and was not re-executed. Aspirational means the list asserts it and this run has no tree to decide it.

`README.md:36` ("Questions in one request run in parallel") is not one of the eight rows. The SDK test fixture sends spam, tone, and quality in one body (`upstream/typesafe-ai/typesafe-sdk-python/tests/test_clients.py:45-53`). That is one request, not a trace that the server ran them in parallel. Left ungraded rather than called parallel.

### Already in this workspace (19 of 71)

Catalogue named none of these SHAs. Prefixes are 12 hex from `git rev-parse HEAD`. Where two trees exist, both prefixes are listed.

| repo | workspace path @ prefix | catalogue line | URL |
|---|---|---|---|
| `typesafe-ai/skills` | `upstream/typesafe-ai/skills@65a39f393687` | 47 | https://github.com/typesafe-ai/skills |
| `typesafe-ai/typesafe-sdk-python` | `upstream/typesafe-ai/typesafe-sdk-python@0ffd094c72ed` | 65 | https://github.com/typesafe-ai/typesafe-sdk-python |
| `typesafe-ai/typesafe-sdk-js` | `upstream/typesafe-ai/typesafe-sdk-js@66880ccded6c` | 66 | https://github.com/typesafe-ai/typesafe-sdk-js |
| `typesafe-ai/system-one-adapter-python` | `system-one-adapter-python@0bb819b85d67` and `upstream/typesafe-ai/system-one-adapter-python@adffc2eab300` (two SHAs) | 67 | https://github.com/typesafe-ai/system-one-adapter-python |
| `AbdelStark/s1-rs` | `s1-rs@b9168979a9be`, `upstream/AbdelStark/s1-rs@b9168979a9be` | 76 | https://github.com/AbdelStark/s1-rs |
| `browser-use/jev-ultrafast` | `jev-ultrafast@452c1ad2dd62`, `upstream/browser-use/jev-ultrafast@452c1ad2dd62` | 89 | https://github.com/browser-use/jev-ultrafast |
| `thruwire/foreman` | `foreman@2c439828b9fe`, `upstream/thruwire/foreman@2c439828b9fe` | 98 | https://github.com/thruwire/foreman |
| `0xNatoshi/jev-codex-router` | `jev-codex-router@8292b5196592`, `upstream/0xNatoshi/jev-codex-router@8292b5196592` | 106 | https://github.com/0xNatoshi/jev-codex-router |
| `gargpratyush/jev-router` | `jev-router@86660a0248eb`, `upstream/gargpratyush/jev-router@86660a0248eb` | 107 | https://github.com/gargpratyush/jev-router |
| `devanshbatham/commit-miner` | `commit-miner@977617ebce07`, `upstream/devanshbatham/commit-miner@977617ebce07` | 109 | https://github.com/devanshbatham/commit-miner |
| `jkudish/jev-mcp` | `jev-mcp@6ec5efc66014`, `upstream/jkudish/jev-mcp@6ec5efc66014` | 140 | https://github.com/jkudish/jev-mcp |
| `NiazMorshed2007/jev-review` | `jev-review@57690af54ef7`, `upstream/NiazMorshed2007/jev-review@57690af54ef7` | 142 | https://github.com/NiazMorshed2007/jev-review |
| `AbdelStark/bicameral` | `bicameral@3bea244b072c`, `upstream/AbdelStark/bicameral@3bea244b072c` | 148 | https://github.com/AbdelStark/bicameral |
| `iammrduncan/typesafe-ai-benchmark` | `typesafe-ai-benchmark@e94fcdaf5058`, `upstream/iammrduncan/typesafe-ai-benchmark@e94fcdaf5058` | 161 | https://github.com/iammrduncan/typesafe-ai-benchmark |
| `anessbelbati/jev-rerank-bench` | `jev-rerank-bench@cd9a35b22aeb`, `upstream/anessbelbati/jev-rerank-bench@cd9a35b22aeb` | 162 | https://github.com/anessbelbati/jev-rerank-bench |
| `bitnovus/jev-spam-eval` | `jev-spam-eval@76ef18305710`, `upstream/bitnovus/jev-spam-eval@76ef18305710` | 163 | https://github.com/bitnovus/jev-spam-eval |
| `anisselbd/jev-phishing-bench` | `jev-phishing-bench@1d56e8c64d02`, `upstream/anisselbd/jev-phishing-bench@1d56e8c64d02` | 164 | https://github.com/anisselbd/jev-phishing-bench |
| `TokenTrim/jev-agent-failure-benchmark` | `jev-agent-failure-benchmark@4d46af795a4a`, `upstream/TokenTrim/jev-agent-failure-benchmark@4d46af795a4a` | 165 | https://github.com/TokenTrim/jev-agent-failure-benchmark |
| `Gaurav-Gosain/jev-sec-bench` | `jev-sec-bench@fdb16b94d375`, `upstream/Gaurav-Gosain/jev-sec-bench@fdb16b94d375` | 166 | https://github.com/Gaurav-Gosain/jev-sec-bench |

`Ying-Kai-Liao/jev-browser` is linked twice (`README.md:90` and `:151`). One repo, one candidate, not two.

Org-only links are not candidates: `https://github.com/typesafe-ai` (`README.md:46`), `https://github.com/browser-use` (`README.md:89`). Live sites, docs, cookbooks, and articles without a `github.com/owner/repo` path are not candidates. `README.md:112` says the smart-home demo source "is slated for GitHub at release" and gives no repo URL.

### Clone candidates (52) — not cloned

Each URL is the catalogue URL. Do not treat this list as proof the repo exists.

| line | URL |
|---|---|
| 69 | https://github.com/nshkrdotcom/typesafe_sdk |
| 70 | https://github.com/joshmn/typesafe-sdk |
| 71 | https://github.com/kieranklaassen/ruby_llm-typesafe |
| 72 | https://github.com/GenieRobot/typesafe-ai-rails |
| 73 | https://github.com/gilljon/typesafe-ai-rs |
| 74 | https://github.com/Twister915/typesafe-ai |
| 75 | https://github.com/AbdelStark/typesafe-rs |
| 77 | https://github.com/pithings/advocaat |
| 78 | https://github.com/jamesward/zio-typesafe-ai |
| 79 | https://github.com/saibimajdi/typesafe-dotnet-sdk |
| 80 | https://github.com/Butochnikov/typesafe-sdk-php |
| 81 | https://github.com/Butochnikov/laravel-typesafe-jev |
| 82 | https://github.com/Gaurav-Gosain/jev-go |
| 83 | https://github.com/AboveColin/jevclient |
| 90 | https://github.com/Ying-Kai-Liao/jev-browser |
| 91 | https://github.com/vlad-terin/jev-browser |
| 92 | https://github.com/awlevin/typesafe-computer-use |
| 93 | https://github.com/droidrun/mobile-jev |
| 94 | https://github.com/kitze/unclutter |
| 95 | https://github.com/AboveColin/HA-Jev |
| 96 | https://github.com/sufianetaouil/every |
| 97 | https://github.com/devagrawal09/jev-review |
| 99 | https://github.com/RomanSlack/jev-drone |
| 100 | https://github.com/phyous/tsai-sc |
| 101 | https://github.com/jarrodwatts/jev-trader |
| 102 | https://github.com/asfarsadewa/human-compiler |
| 103 | https://github.com/ChetasLua/jevmeter |
| 104 | https://github.com/santos-sanz/jev-audio-beeper |
| 105 | https://github.com/TarunTomar122/jev-askable-arm |
| 108 | https://github.com/teyhouse/jev-secret-detection |
| 110 | https://github.com/vinilana/jev-eval-agent |
| 111 | https://github.com/reachjalil/jevlogs |
| 121 | https://github.com/fhshaik/typesafe-mario |
| 122 | https://github.com/lukaske/jev-doom-agent |
| 123 | https://github.com/mizchi/jev-gomoku |
| 124 | https://github.com/joshlarsen/jev-t-rex-runner |
| 125 | https://github.com/siroccomask/snake-jev |
| 131 | https://github.com/phureewat29/got-jev |
| 132 | https://github.com/lbotinelly/jev-little-airways |
| 139 | https://github.com/vercel/eve |
| 141 | https://github.com/blakestone-x/jev-mcp |
| 143 | https://github.com/itsmostafa/typesafe-mcp |
| 144 | https://github.com/DevMortimer/pi-typesafe |
| 145 | https://github.com/y0usaf/pi-jev |
| 146 | https://github.com/DevMortimer/pi-warden |
| 147 | https://github.com/jomatsu/pi-jev-auto-mode |
| 149 | https://github.com/shantanugoel/ask-jev-skill |
| 150 | https://github.com/samtay32/jev-system-architect |
| 157 | https://github.com/vinnylarouge/jevlike |
| 158 | https://github.com/TheoLeeCJ/openjev |
| 159 | https://github.com/NullPo-jp/PocketJev |
| 160 | https://github.com/Mapika/decider |

**T3: PASS.** Eight claims classified with a deciding file:line (floor is five). Every GitHub project link was checked for a SHA (zero named). Clone candidates are the 52 repos whose origin was not among the 46 workspace clones. None were cloned.

## Other test ids

| id | status | reason |
|---|---|---|
| T2 | NOT-APPLICABLE | No suite. `git ls-tree -r --name-only HEAD` is five files, none a test runner. A planted typo in a `/tmp` copy cannot go RED because nothing executes the list. That is "no suite", not "suite unable to fail". |
| T4 | NOT-APPLICABLE | Catalogue profile is T1+T3 (`docs/PLAN-DEEP-KIT-20260922.md:427-428`). Assignment: no live call. T4 bar file was not used and not rewritten. |
| T5 | NOT-APPLICABLE | Floor arms apply to seat/benchmark. This clone has no labelled rows. |
| T6 | NOT-APPLICABLE | Incumbent arm applies to seat/benchmark. No live call. |
| T7 | NOT-APPLICABLE | Calibration applies to seat/benchmark. N=0. |
| T8 | NOT-APPLICABLE | Stability applies to seat/benchmark. N=0. |
| T9 | NOT-APPLICABLE | Fault behaviour applies to SDK/client/tool clones. This tree has no client. |

T4–T9 are excluded by class, not skipped after a failed command. If a reader still wants the four earned-label fields for T4: command not issued; verbatim output none; cause `docs/PLAN-DEEP-KIT-20260922.md:427-428` (catalogues run T1+T3) and the assignment sentence "No live call"; routes tried: (1) class table, (2) assignment text plus "Do not clone them". No second command was run because a live call would violate the assignment.

## Evidence level

No row in this receipt is a test, an oracle, or a live N. Lane is local file and git inspection on `Joshs-Mac-Studio.local`, clock `2026-09-23T03:16:09Z`, model none (zero Jev calls, zero other model calls).

| number | level | lane, N, date, model |
|---|---|---|
| SHA `ef193004eba48e83339a6e7498e70530badd23a5`, clean status | command observation, not a test | `git rev-parse` / `git status` on `awesome-jev`, N=1 tree, 2026-09-23T03:16:09Z and again after the receipt write, model none |
| 71 repos, 0 commit pins | command observation | regex on `README.md`, N=71 unique `owner/repo` links, same clock, model none. Re-run printed `PASS ... repos 71 commit_pins 0` |
| 46 workspace clones, 19 present, 52 absent | command observation | `git remote get-url origin` on every `.git` under the jev tree and `upstream/`, N=46 clones, same clock, model none |
| 7.1 s, 7.073 s, 7.092 s | quoted maintainer text, not remeasured | `jev-ultrafast` README/docs at prefix `452c1ad2dd62`, N not re-counted here (clone says six runs for the median), file date not re-derived, model none in this run |
| 62.6%, 81.3%, n=2000 | quoted file, not recomputed | `jev-phishing-bench` README:11-13 and `results/metrics.json:3,196,1396` at prefix `1d56e8c64d02`. That file's own `jev_model` field is `jev-1.13.0` (`metrics.json:297`); this run did not call it. Generated-at in that file: `2026-09-17T09:38:32Z` (`metrics.json:2`) |
| SDK field names | schema read, not a served response | `typesafe-sdk-python` at prefix `0ffd094c72ed`, N=3 answer classes, clock above, model none |


## T10 — verdict

Result class: **none**. SELF / FLOOR / INCUMBENT are measurement classes. This clone measures nothing. Recording one of the three would invent a result. N=0 Jev calls. N under 20 is a smoke, not a certification; this run is below that and is not a smoke of the model either.

RULEBOOK tier per claim: see the T3 table. Pin, license, clean status, 71-repo count, and zero commit pins are [Verified]. SDK field names are [Verified] as schema, not as served answers. Numbers read out of `jev-ultrafast`, `jev-phishing-bench`, and `jev-spam-eval` are [Maintainer claim] of those clones, inspected at SHAs the catalogue did not name. The three uncloned blurbs are [Maintainer claim] of the list only.

NO-CLAIM: this receipt does not claim Jev accuracy, cost, latency, calibration, or that any listed project behaves as its blurb says, except the file inspections in rows 1–5, and those inspections are not catalogue pins. It does not claim the 52 absent repos exist, build, or match their sentences. It does not claim HTTP 200 for any link. It does not claim the two `system-one-adapter-python` trees are the same commit. It does not claim workspace clones whose origins were not in the 71 (`awesome-jev-by-typesafe`, `awesome-typesafe`, `fast-jev-compaction`, `jev-align`, `jev-benchmark`, `pi-subagents`, `skillranker`) are missing from the list for a reason; they simply did not match a catalogue URL.

## Boundary

Catalogue text plus local git metadata and file reads. No live Jev call. No `infisical` run. No clone, fetch, or HTTP probe. No defect planted. `awesome-jev` not edited. `EVAL.md` not edited. Prior `EVAL.md:61-63` (15/15 links HTTP 200) was not used as a pass.
