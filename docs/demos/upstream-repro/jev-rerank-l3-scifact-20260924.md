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
   be reached through the tool; it is unit-covered.
3. **Keyless:** qid 36's query and its first 3 passages. Expect `ordered=false reason=unconfigured
   NOT_RUN`, with the input order returned.

**Spend.** Counted from the frames: calls equal the passages scored, and Jev bills input tokens only,
at $0.042 per million. `JevScoreResult` returns no usage, so tokens are not stated.
