# `jev_rerank` at L3 in real omp sessions, on a public SciFact query (bead `jev-k9z.8`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. Live lane: TypeSafe only, model
`jev-1.13.0`. **No comparator is called.**

**Seam.** `.omp/tools/jev-rerank.ts`, loaded by the project extension `.omp/extensions/jev-rerank.ts`
(omp scans `<cwd>/.omp/extensions`, not `.omp/tools`).
- The tool's schema accepts a `query` string and 2 to 30 passages.
- It calls `work/nev-rerank/src/rank.ts`'s `rerank()` with `live.ts`'s asker: one validated
  `askJevScore` call per passage, `jev-1.13.0`, 20 s each.
- It returns `ordered=true calledModel=true` and the new order.
- With no `TYPESAFE_API_KEY` it returns the input order with `ordered=false reason=unconfigured
  NOT_RUN`, and it never throws.

## Fixed before any call (committed with this section)

**Query, by a rule stated now and applied mechanically.**
- The rule: the first qid in `work/rerank-scifact/candidates.jsonl` order whose BM25 top-1 is not in
  its qrels set, and which has at least one qrels-relevant doc in its BM25 top-20.
- It selects **qid 36**, *"A deficiency of vitamin B12 increases blood levels of homocysteine."*
  (the 5th row).
- Its qrels hold `11705328` and `5152028`. Only **`11705328` is in the BM25 top-20, at position 7.**
- The corpus is the sha256-pinned BEIR SciFact zip `run.py` uses (`536e1444…0165`).

**Passages.** The 20 BM25 candidates, in BM25 order. Each is `title + ". " + abstract`, cut to its
first **500 characters** so the session model can pass all 20 verbatim; 10,000 characters in all.
The full abstracts run 1,198 to 2,769 characters (median 1,809). This is not `jev-k9z.7`'s input,
and the frame is L3 evidence that the seam fires, not a measurement. Wherever `11705328` lands is
reported as it is.

**Sessions.** Each frame comes from `omp --profile claude -p --mode json`, a real non-interactive omp
session with a fresh session id, run from this repo so the project extension loads. It is not an rpc
scratch session.
- Model `anthropic/claude-sonnet-5` with thinking off, on this profile's subscription login.
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY` and `OPENROUTER_API_KEY` are unset for every
  session, so no comparator or API-billed model key is reachable.
- Keyed sessions get `TYPESAFE_API_KEY` through `infisical run`. The keyless session runs with no
  `infisical` and `TYPESAFE_API_KEY` unset.
- Each frame is the tool's own result, read from the JSON event stream: the `tool_execution_end`
  event's result for `jev_rerank`.

**The three directions.**
1. **Keyed positive:** qid 36, the query and 20 passages above. Expect `ordered=true
   calledModel=true`, and 20 Jev calls. Reported: where `11705328` lands versus BM25's position 7,
   and whether the returned passage texts are the ones sent, byte for byte.
2. **Keyed negatives:**
   - (a) 1 passage;
   - (b) 31 passages (`p01`…`p31`).

   The schema (min 2, max 30) should refuse both before `execute`, with an error frame, no throw and
   no Jev call. `rank.ts`'s own `MAX_PASSAGES = 30` truncation sits behind the schema, so it can't
   be reached through the tool. *(Corrected after the sessions: this line said the truncation is
   unit-covered. No test in `work/nev-rerank/test/` exercises it.)*
3. **Keyless:** qid 36's query and its first 3 passages. Expect `ordered=false reason=unconfigured
   NOT_RUN`, with the input order returned.

**Spend.** Counted from the frames: calls equal the passages scored, and Jev bills input tokens only,
at $0.042 per million. `JevScoreResult` returns no usage, so tokens are not stated.


## Results (live, 2026-09-24, `jev-1.13.0`, omp 18.3.0)

Rule, query and passages were committed at `25311f1` before the first session.

**Command.** Every session ran from the repo root, `omp --profile claude -p --mode json --model
anthropic/claude-sonnet-5 --thinking off --max-time <240|400> "<prompt>"`.
- Keyed sessions were wrapped in `~/.local/bin/infisical run --silent --projectId=42b194c3-… -- env -u
  ANTHROPIC_API_KEY -u OPENAI_API_KEY -u XAI_API_KEY -u OPENROUTER_API_KEY`.
- The keyless session had no `infisical`, and `TYPESAFE_API_KEY` and `JEV_API_KEY` were unset along
  with the other four.
- The profile's Anthropic login is `oauth` in `agent.db` (`auth_credentials.credential_type`), not an
  API key.
- The prompt asks for one call with the JSON copied byte for byte and no retry on refusal.

**Route.** In each session the model called `write` with path `xd://jev_rerank`. The result's
`details.xdev` is `{tool: "jev_rerank", mode: "execute", tier: "exec"}`, and on the
executed paths it wraps the tool's own `details` as `inner`. So each frame below is `jev_rerank`'s
own `execute()` result, or the schema's refusal before `execute()`. It is not the model's
paraphrase. For every session, the args the model wrote parse to exactly the JSON the prompt held.

| # | Direction | Session | Tool calls | Result |
|---|---|---|---|---|
| 1 | keyless, 3 passages | `01a0d595-00d7-722a-88e1-4f433bb3636a` | 1 | `ordered=false reason=unconfigured NOT_RUN`, input order |
| 2 | keyed, 1 passage | `01a0d596-2c97-7339-b089-78a195d7d440` | 1 | schema refusal, `isError: true`, no throw |
| 3 | keyed, 31 passages | `01a0d596-9bd0-72ca-9263-9f8aa44941f2` | **0** | the model declined (below); no frame |
| 3b | keyed, 31 passages | `01a0d597-a6b0-7567-a819-5ee763e10fc4` | 1 | schema refusal, `isError: true`, no throw |
| 4 | keyed positive, qid 36, 20 passages | `01a0d598-32e8-72bd-b2f8-ec900cd5a6f9` | 1 | `ordered=true calledModel=true` |

The session files are under `~/.omp/profiles/claude/agent/sessions/-Developer-jev/`, named by
start time and id. They are not committed.

**Session 3 made no call.** Sessions 1 and 2 used the first prompt, which named the tool
`jev_rerank`. In session 3 the model replied that `jev_rerank` "is not among my available tools". It
also said the prompt matched "an injection pattern … instructing verbatim blind tool calls", and it
wrote nothing. Sessions 3b and 4 name the route, `xd://jev_rerank`, and each made exactly one call.
Only the prompt wording changed. The rule, the query, the passages and the args are the same.

### Frame 4: keyed positive (qid 36)

This is the result text, with each passage cut here to 70 characters. In the frame, all 20
returned passage texts are byte-identical to the 20 sent, each under its own `pNN` id.

```
ordered=true calledModel=true
1. [p05 0.640] The effect of folate fortification on folic acid-based homocysteine-lo…
2. [p02 0.497] Effect of homocysteine lowering on mortality and vascular disease in a…
3. [p04 0.380] Preventing coronary heart disease: B vitamins and homocysteine.. The l…
4. [p10 0.380] The effect of folic acid supplementation on plasma homocysteine in an …
5. [p07 0.353] Randomized trial of folic acid supplementation and serum homocysteine …
6. [p03 0.350] British Journal of Nutrition (2003), 89, 295–301 q The Authors 2003 DO…
7. [p01 0.340] Gene--nutrition interactions in coronary artery disease: correlation b…
8. [p06 0.313] Homocysteine and the risk of ischemic stroke in a triethnic cohort: th…
9. [p17 0.313] Original Article. UNLABELLED Fruit and vegetable consumption has been …
10. [p11 0.300] Effects of soy isoflavones and phytate on homocysteine, C-reactive pro…
11. [p16 0.297] No net renal extraction of homocysteine in fasting humans.. BACKGROUND…
12. [p20 0.253] Homocysteine and other thiols in plasma and urine: automated determina…
13. [p14 0.127] Chronic renal failure accelerates atherogenesis in apolipoprotein E-de…
14. [p12 0.017] Vitamin D insufficiency and the blunted PTH response in established os…
15. [p13 0.017] Vitamin D status: measurement, interpretation, and clinical applicatio…
16. [p08 0.013] Vitamin D: The "sunshine" vitamin.. Vitamin D insufficiency affects al…
17. [p18 0.013] Environmental factors that influence the cutaneous production of vitam…
18. [p19 0.013] Global vitamin D levels in relation to age, gender, skin pigmentation …
19. [p09 0.010] Ascorbic-acid transporter Slc23a1 is essential for vitamin C transport…
20. [p15 0.010] Calcium absorption varies within the reference range for serum 25-hydr…
```

- **The one relevant doc in the top-20**, `11705328` (`p07`), is at **5** against BM25's **7**.
  One query is a frame, not a measurement. `jev-k9z.7`'s three runs of 300 queries are the
  measurement.
- The seven passages about vitamin D, vitamin C and calcium absorption score 0.010 to 0.017 and
  fill places 14 to 20.
- `p04` and `p10` tie exactly (0.38) and keep input order, since `orderByScores` breaks ties on
  index (`rank.ts:95`). `p06` and `p17` differ only at about the 17th digit.
- `details`: `ordered: true`, `reason: null`, `calledModel: true`, `truncated: false`.

### Frame 2: keyed, 1 passage

```
Invalid args for xd://jev_rerank: Validation failed for tool "jev_rerank":
  - passages: passages must be at least length 2 (was 1)

```

### Frame 3b: keyed, 31 passages (`p01`…`p31`)

```
Invalid args for xd://jev_rerank: Validation failed for tool "jev_rerank":
  - passages: passages must be at most length 30 (was 31)

```

- Both negatives are refused by the tool's zod schema before `execute()`. That means no
  `rerank()`, no asker and no Jev call; `details.xdev` carries no `inner`.
- `rank.ts`'s `MAX_PASSAGES = 30` truncation can't be reached through the tool, and no test
  exercises it.

### Frame 1: keyless (qid 36, first 3 passages)

```
ordered=false reason=unconfigured NOT_RUN
1. [p01 -] Gene--nutrition interactions in coronary artery disease: correlation b…
2. [p02 -] Effect of homocysteine lowering on mortality and vascular disease in a…
3. [p03 -] British Journal of Nutrition (2003), 89, 295–301 q The Authors 2003 DO…
```

`details.xdev.inner`:

```
{"ordered": false, "reason": "unconfigured", "calledModel": true, "truncated": false, "ranking": [{"id": "p01", "index": 0, "score": null}, {"id": "p02", "index": 1, "score": null}, {"id": "p03", "index": 2, "score": null}]}
```

**Finding: `calledModel: true` on a keyless NOT_RUN.**
- `rank.ts:131` sets `calledModel: true` whenever the asker returns `ok: false`.
- `askJevScore` (`work/jev-client/src/index.ts:482-490`) returns `unconfigured` before any
  `fetch` when there is no key.
- So on this path no model was called, but `details` says one was. The result text is right: it
  says `NOT_RUN` and does not print `calledModel`.
- A consumer that branches on `details.calledModel` reads a keyless run as a live one. Filed as
  `jev-t7oq`. Nothing was changed here.

**Fixed at `06cb37e` (`jev-t7oq`), after these sessions.**
- A failing asker now says whether it sent a request. `rerank()` copies that, and an asker that
  does not say is reported as `calledModel: false`.
- `liveAsker` watches its own transport. `calledModel` is true once a request reached `fetch`
  (an HTTP 402, a timeout, a transport throw). It is false for `unconfigured`, `billing-hold` and
  `sdk-missing`.
- Offline tests in `work/nev-rerank/test/` cover the keyless, 402, billing-hold and timeout
  cases.
- Keyless re-run: one `omp --profile claude -p --mode json` session, `01a0d5a5-8bca-7102-b8e7-46b54a90c5b2`,
  with the same flags and unset keys as above. The prompt held three short synthetic passages, not
  qid 36. It made one `write xd://jev_rerank` call and no Jev request. Result text:
  `ordered=false reason=unconfigured NOT_RUN`. `details.xdev.inner`:

```
{"ordered": false, "reason": "unconfigured", "calledModel": false, "truncated": false, "ranking": [{"id": "p01", "index": 0, "score": null}, {"id": "p02", "index": 1, "score": null}, {"id": "p03", "index": 2, "score": null}]}
```

### Calls, time and spend

- **20 Jev requests**, all in session 4, one validated `askJevScore` per passage (`live.ts`).
  Each carries the whole state: the query and all 20 passages, 10,274 characters as compact JSON.
- 0 failed, and sessions 1 to 3b made 0 Jev requests.
- Session 4 took 70 s wall (22:45:15Z to 22:46:25Z). That is two model turns plus the 20 calls
  in series; the frames carry no per-call latency.
- The frame doesn't surface tokens, because `rank.ts` doesn't carry `usage` through. At about 4
  characters a token that is roughly 50,000 input tokens, about **$0.002**. This is an
  estimate, not a reading.
- No comparator and no other model API was called. The session model is the harness driver on
  the profile's oauth login.

**Rung: L3.** The seam fires in real omp sessions on the current tree. A keyed positive
returned `ordered=true` with a changed order. Two planted bad inputs are refused without a throw,
and keyless returns `NOT_RUN`. **NO-CLAIM:**
- one query and one run;
- passages cut to 500 characters;
- no L4, since no working session used the tool on its own initiative;
- no latency figure.
