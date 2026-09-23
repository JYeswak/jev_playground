# jev-codex-router W7.0 — 2026-09-23

Clone: `/Users/josh/Developer/jev/jev-codex-router`. Pin: `8292b519659280884627a962c826ac7721136a64` (short `8292b5196592`). Commit date: `2026-09-17 19:08:06 +0200`, subject `docs: drop the version suffix from the picker name in AGENTS.md too`. Class: tool/integration. Tests run: T1 T2 T3 T4 T9 T10. Worker: `W70Codex`. Host: `Joshs-Mac-Studio.local`, Darwin 25.5.0 arm64, user `josh`. Run start: `2026-09-23T03:16:08Z`.

T4 bar, committed before this call: `docs/demos/upstream-repro/w70-t4-bar-20260922.md` at `da2a785db92e15f314aa47829015d84f0a038d97` (`2026-09-22 21:14:20 -0600`). Not retuned. Model pin required by that bar: `jev-1.13.0`.

Prior receipts (`routers-20260918.md`, `router-savings-inverts-20260919.md`) were not used as passes.

| id | status | one line |
|---|---|---|
| T1 | PASS | Pin matches, MIT, tree clean before and after, profiles unset, runtimes recorded. |
| T2 | NOT-APPLICABLE | No test suite. Search below. CI `compileall` is a syntax gate, not a suite; a `/tmp` plant turns that gate RED. |
| T3 | PASS | Six claims classified from README/AGENTS against this run. |
| T4 | PASS | Smoke only. N=12 `<` 20. No accuracy claim. POC client, clone fixture, request named `jev-1.13.0`, 12/12 schema-valid, process alive. |
| T9 | FAIL | Server handler coerces missing key, HTTP 500, malformed JSON, malformed choice, and a dropped connection into an astra route and returns HTTP 200. Host survives. |
| T10 | PASS | Verdict recorded. Result class not earned. |

## T1 — pin and environment

Command: `git -C jev-codex-router rev-parse HEAD && git status --porcelain=v1 && git log -1 --format='%H%n%ci%n%s'`.

Verbatim pin line: `8292b519659280884627a962c826ac7721136a64`. Porcelain before the run: empty. Porcelain after the run: `0` lines. Branch: `## main...origin/main`.

License: `LICENSE:1` `MIT License`. Copyright `LICENSE:3` Thibault Saint-Jean, 2026.

Environment after `unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR`: all three `<unset>`. `omp/18.2.10` at `/Users/josh/.bun/bin/omp`. No omp command was run.

Runtimes: `python3` is `Python 3.9.6` (below the prerequisite at `AGENTS.md:39`, Python ≥ 3.11). `python3.11` is `Python 3.11.14`. `python3.12` is `Python 3.12.13`. This run used `python3.12`. `python3.13` is absent.

## T2 — own suite

Search, three routes:

1. `git ls-files` — 19 tracked paths. No `test/`, `tests/`, `pytest`, `tox`, `Makefile`, `pyproject.toml`, or `requirements`. The only workflow is `.github/workflows/ci.yml`.
2. Grep of the clone for `pytest|unittest|def test_` — no test definitions. The only automated command is `ci.yml:16-17`: `python -m compileall -q server poc`.
3. README and AGENTS name `python3 server/jev_server.py`, `python3 poc/backtest_savings.py`, and a curl health check. None is a suite with pass/fail/skip counts.

NOT-APPLICABLE: there is no suite, so there are no pass/fail/skip counts to report.

Adjacent, not a suite: the CI syntax gate on the pin, `python3.12 -m compileall -q server poc`, exit `0`. Same command in `/tmp/jev-codex-router-w70` after deleting the colon on `poc/route_poc.py:87` exited `1`. Verbatim:

```
File "poc/route_poc.py", line 87
    def post_json(url, key, body, attempts=3)
                                             ^
SyntaxError: expected ':'
```

The plant was only in `/tmp`. The clone was not edited.

## T3 — claims

| # | claim | status | decides it |
|---|---|---|---|
| 1 | Fail-open: any Jev error keeps the turn alive (`README.md:38`, `AGENTS.md:199-200`) | demonstrated | Isolated handler log: `jev_error:HTTPError`, `jev_error:JSONDecodeError`, and `jev_error:RemoteDisconnected` each returned HTTP 200 and `model=gpt-6-astra` (`server/jev_server.py:717-718`). [Verified] |
| 2 | Decision costs ≈ $0.00003 and ≈ 0.6 s (`README.md:9`, `AGENTS.md:198`) | partial | Latency measured on the smoke (below). Dollar figure not priced: the response has token counts, and this receipt does not invent a rate. [Verified latency; cost remains Maintainer claim] |
| 3 | Confidence below 0.5 falls back to sol, not astra (`README.md:56-58`) | demonstrated as policy | `jev_server.route("gpt-5.6-luna", "low", 0.1, None)` returned `["gpt-5.6-sol", "low", "default", "hold(sol)"]` (`server/jev_server.py:235-246`). The −80% savings sentence was not re-measured. [Verified policy; savings corollary Maintainer claim] |
| 4 | −60% vs full-frontier on 237 turns (`README.md:11-12`, `BACKTEST.md:3-4`) | partial | Committed sample `poc/backtest-sample-results.json:4` `turns: 237`, `:32` `savings_vs_astra_pct: 59.9`, `:15` `871.48` vs `:12` `349.29`. `(871.48-349.29)/871.48 = 0.599`. Classifier not re-run. [Maintainer claim, artifact agrees with the prose] |
| 5 | Send `"model": "jev-latest"` or Jev returns 422 (`AGENTS.md:192`) | demonstrated as the default; stale against the pin | `server/jev_server.py:78` `MODEL = "jev-latest"`. POC default `poc/route_poc.py:162` is the same. The server has no pin flag. A body that omitted `model` was not sent. [Verified default] |
| 6 | Kill switch relays astra and does not call Jev (`AGENTS.md:155-156`) | demonstrated | Isolated `OFF_PATH` set: log `gate=off`, `model=gpt-6-astra`, `jev_ms=null`, HTTP 200 (`server/jev_server.py:690-691`). User `~/.codex` was not touched. [Verified] |

Loopback bind (`README.md:217`, `server/jev_server.py:71` `LISTEN = ("127.0.0.1", 4319)`) was observed on the imported constant and on the isolated server. Not one of the five required rows; recorded so the security sentence is not left unread.

## T4 — live call

Bar used: the committed file above. Not rewritten.

Client: `poc/route_poc.py` `post_json` (`:87-103`) and `validate_choice` (`:105-115`). Own state: `poc/tasks.json` (12 rows, clone-authored, not written for this run). The server client was not the live caller: `MODEL` is hardcoded `jev-latest` (`server/jev_server.py:78`), which fails the pin, and `Handler._post` relays to the local Codex router (`:804-822`).

Command:

```
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- python3.12 /tmp/w70-codex-t4.py
```

The driver imports the clone and sends `{"model":"jev-1.13.0","state":{"task","signals"},"questions": questions()}` — the same body `run()` builds at `poc/route_poc.py:126-127`. Key presence was a boolean. The key was not printed.

Verbatim start and end:

```
{"event": "start", "n": 12, "model": "jev-1.13.0", "default_model": "jev-latest", "key_present": true, "api": "https://api.typesafe.ai/v1/systemone", "pid": 87454}
{"event": "done", "n": 12, "threw": 0, "schema_valid": 12, "p50_ms": 333.7, "p95_ms": 942.7, "alive": true, "pid": 87454, "smoke": true}
```

Per call, request model `jev-1.13.0`, schema valid against the clone's own `validate_choice` for both questions, process still pid 87454 at the end:

| id | ms | in_tok | out_tok |
|---:|---:|---:|---:|
| 1 | 942.7 | 713 | 113 |
| 2 | 333.7 | 697 | 113 |
| 3 | 437.4 | 709 | 113 |
| 4 | 295.1 | 711 | 112 |
| 5 | 392.6 | 707 | 112 |
| 6 | 424.6 | 702 | 112 |
| 7 | 342.3 | 718 | 112 |
| 8 | 395.9 | 700 | 113 |
| 9 | 248.3 | 719 | 111 |
| 10 | 274.5 | 713 | 111 |
| 11 | 301.0 | 711 | 111 |
| 12 | 289.6 | 713 | 113 |

Sums copied from those finite counts: input `8513`, output `1346`. Cost not computed. Response keys were `answers`, `model`, `usage`. The echoed `model` string was not copied; the request field was.

p50/p95 method, N=12 ≥ 5: nearest-rank index `ceil(p*N)-1` on the sorted latencies. Sorted: `248.3, 274.5, 289.6, 295.1, 301.0, 333.7, 342.3, 392.6, 395.9, 424.6, 437.4, 942.7`. p50 index 5 = `333.7`. p95 index 11 = `942.7`. Even-n median would be `(333.7+342.3)/2 = 338.0`; that is not what the driver printed.

N=12 is a smoke, not a certification. No accuracy claim. No positive-class prevalence: a 3-way route has no positive class declared by the bar, and inventing one would be an accuracy claim.

Choices were returned and were schema-valid. They are not scored here.

## T9 — fault behaviour

Two clients. The product path is `server/jev_server.py`. The POC HTTP helper refuses. The product wrapper coerces. Host survived every arm (pid printed, exit of the driver was the JSON printer, not a crash of the handler).

POC `post_json` against `127.0.0.1` (`python3.12 /tmp/w70-codex-t9.py`). urlopen timeout patched to 0.3 s so the timeout arm did not wait 30 s. Verbatim messages:

- timeout: `RuntimeError` `connection failed: TimeoutError('timed out')` in 350.3 ms
- 429, one attempt: `RuntimeError` `HTTP 429; no routing decision.` in 5.2 ms
- 500: `RuntimeError` `HTTP 500; no routing decision.` in 3.2 ms
- 200 + `not-json`: `RuntimeError` `connection failed: JSONDecodeError(...)` in 6.2 ms
- 429, two attempts: same `HTTP 429` refusal after 587.8 ms (it retried, then refused)

`validate_choice` on `{}`, a choice with no probabilities, `choice=nope`, and a probability map missing two tiers: each raised `ValueError: invalid choice answer: ...`. No coercion.

Missing key, route 1: `HOME=/tmp/w70-codex-empty`, `TYPESAFE_API_KEY` unset, `route_poc.load_key() == ""`, `run()` printed `!! TYPESAFE_API_KEY not found (env, ~/.hermes/.env, ~/.jev.env). Use --dry to validate payloads.` and returned `2`. No score. Route 2: the same function reads `~/.hermes/.env` then `~/.jev.env` then the environment (`poc/route_poc.py:71-85`); under that HOME both files were absent.

Missing depth, executed through `run()` with `post_json` replaced by a local fake that returned a valid tier and `"depth": {}`: verbatim `depth=medium -> gpt-5.6-luna @max [priority]` and `run_exit 0`. That is `poc/route_poc.py:137` coercing a missing depth to `"medium"` and still routing. The same run printed `≈ $0.00000`. That dollar figure is the client's `total_tok/1e6*0.042` (`:155`). Not a measured cost.

Server `call_jev` against the same local fault server, timeout 0.3 s: `TimeoutError: timed out`, `HTTPError: HTTP Error 429`, `HTTPError: HTTP Error 500`, `JSONDecodeError`. The function raises. It does not coerce. `MODEL` observed as `jev-latest`.

Server handler, the product path, executed under `HOME=/tmp/w70-codex-home` so `STATE`, the log, and the kill-switch file were not the user's `~/.codex`. Stub router on another free port. Fault Jev on another free port. Log `/tmp/w70-codex-home/.codex/codex-router/jev-router-live.jsonl`, six lines, all HTTP 200 to the caller:

```
gate=no_key_or_task model=gpt-6-astra jev_ms=null
gate=jev_error:HTTPError model=gpt-6-astra
gate=jev_error:JSONDecodeError model=gpt-6-astra
gate=apply tier=null conf=0.99 model=gpt-6-astra
gate=jev_error:RemoteDisconnected model=gpt-6-astra
gate=off model=gpt-6-astra jev_ms=null
```

The fourth line is the malformed-choice arm: Jev returned `choice=nope` with `confidence=0.99`. `server/jev_server.py:710` drops a choice not in `TIERS`, then `route(None, ...)` (`:251`) returns astra with `gate=apply`. A malformed body became a frontier route, not an error. That is the fail.

The timeout arm in that handler drive closed the socket, so the handler saw `RemoteDisconnected`, not `TimeoutError`. Route 2 for timeout is the direct `call_jev` arm above, which raised `TimeoutError` and did not coerce. The handler's `except Exception` (`:717-718`) is the line that assigned astra for the three exception types in the log. A handler-level `TimeoutError` was not the string in the log.

`route(None, "low", 0.9, None)` returned `["gpt-6-astra", "low", "default", "apply"]`. Same coercion, called directly.

T9 fails because the running server refuses nothing: missing key, 5xx, malformed JSON, a bad choice, and a dropped connection all become a served route. The host process surviving is necessary and not sufficient.

## T10 — verdict

Result class: not earned. This profile does not run T5 or T6, so FLOOR and INCUMBENT were not measured. N=12 forbids an accuracy class. Do not read the smoke as SELF.

NO-CLAIM: no routing accuracy, no savings on any session corpus, no dollar cost, no end-to-end Codex picker proof, no claim that `jev-latest` and `jev-1.13.0` agree. The server's live call to `api.typesafe.ai` was not made.

What a non-author should re-run:

```
cd /Users/josh/Developer/jev/jev-codex-router && infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- python3.12 poc/route_poc.py --model jev-1.13.0
```

That command uses the clone's CLI, the clone's `poc/tasks.json`, and the pin. N=12. It is a smoke. Its agreement fraction and its `$` print are not a certification and not a cost.

## Boundary

Clone not edited. `git status --porcelain` was empty before and after (`0` lines). `EVAL.md` not edited. No secret printed. User `~/.codex/codex-router` kill switch, decision log, and caller secret were not read or written; the handler drive used `HOME=/tmp/w70-codex-home`. No Codex router on `:4202` was called. `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` were unset; omp was not invoked. T5 T6 T7 T8 were out of this assignment. The 237-turn classifier was not re-run. The server path cannot name `jev-1.13.0` without an edit, so it was not the live caller.
