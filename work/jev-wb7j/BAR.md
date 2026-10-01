BAR (WildCarp, 2026-10-01, committed BEFORE reading outcome data):

Population: (user-turn prompt, one injected memory item) pairs from
-Profiles/*/agent/sessions/-Developer-jev/*.jsonl, mtime last 7 days
(2026-09-24..10-01). Memory item = one bullet/fact inside an injected
block: `<memories>...</memories>` (Mnemopi) or `Task-relevant local EE
memories` block.

Step 1 (keyless): census = turns with injection, blocks/turn,
tokens/turn (tokens = len chars // 4, stated estimator). Then sample
100 pairs, simple random, seed 42. If fewer than 100 pairs exist, use
all and report N. I label each RELEVANT/IRRELEVANT blind to Jev scores
(labels completed before any live call is issued). Rule: RELEVANT if a
competent engineer would use that memory to answer or act on that
prompt; borderline -> RELEVANT (conservative toward keeping).

Step 2 (live, bounded): one Jev Noul per pair on jev-1.13.0, state =
{prompt, memory}, question = `is this memory relevant to the current
request?`. Budget: max 110 calls (100 + up to 10 retries, retryable
429/5xx only per SDK RetryPolicy); stop on 401/402/403; checkpoint one
row per call (model, tokens, latency, status); spend stated at $0.042/M
input tokens. Key via infisical, never in tree/logs.

Decision rule (pre-committed, no tuning on outcomes): DROP iff
noul < 0.5. Invalid/failed answers count as KEEP (fail safe).

Metrics on the 100: precision_of_drop = P(human IRRELEVANT | Jev DROP);
token_reduction = tokens(DROPPED) / tokens(all sampled memories).

PASS iff precision_of_drop >= 0.90 AND token_reduction >= 0.40.
Else FAIL. Either way: report full confusion matrix + spend.
If PASS: file a design bead for the hook point. NO-CLAIM: no hook
built in this bead. Verifier CyanPeak re-runs and closes.
