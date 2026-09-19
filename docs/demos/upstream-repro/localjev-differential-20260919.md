# LocalJev differential oracle

Workdir: /Users/josh/Developer/jev/work/p2-localjev
Source clone: /tmp/localjev (untouched)
Source revision: 3f23e36e1a3bff46c7e83e8e3781d3512bc82021

## Preregistered bar

Over >= 40 pinned questions drawn half from cases where real Jev answered confidently correct and half from cases where it answered confidently wrong or near-0.5, LocalJev is a USABLE SUBSTITUTE if (a) its argmax agrees with real Jev on >= 80% of cases, AND (b) the mean absolute probability difference is <= 0.15. Missing either => NOT-SUBSTITUTE, an equally acceptable result.

Feasibility arm: the safety-incident case must be classified true and the cold-meal case false. If either fails, report BROKEN-HARNESS/UNUSABLE-BACKEND rather than a substitutability verdict.

## Setup

- bun install: PASS; 9 packages installed.
- bun test: 19 pass, 0 fail.
- bun run typecheck: PASS.
- Local oMLX GET /v1/models: incoai/Qwen3.8-27B-Splash available.
- LocalJev GET /ready: status ready, upstream_model incoai/Qwen3.8-27B-Splash.

SDK retarget feasibility probe using client.systemOne state/questions and noul:

- Safety incident: p=0.990, correct.
- Cold meal: p=0.000, correct.

## Pinned differential cases

Cases came from saved real Jev outputs in jev-spam-eval/results/results_lingspam_criteria_all.jsonl using the bare spam probability and matching real labels. Selection: sort by file; first 20 real-argmax-correct cases with p<=0.10 or p>=0.90, then first 20 wrong or 0.40<=p<=0.60 cases. Pinned JSON SHA-256: 066739145134926c8a5fec2b14c7a91a38d7db67b4c804e52dd012de338cfee4.

| File | Label | Real p | Arm |
|---|---|---:|---|
| part1/3-1msg1.txt | ham | 0.05 | confident-correct |
| part1/3-1msg2.txt | ham | 0.09 | confident-correct |
| part1/3-378msg1.txt | ham | 0.10 | confident-correct |
| part1/3-378msg2.txt | ham | 0.03 | confident-correct |
| part1/3-378msg3.txt | ham | 0.04 | confident-correct |
| part1/3-378msg5.txt | ham | 0.03 | confident-correct |
| part1/3-379msg1.txt | ham | 0.08 | confident-correct |
| part1/3-379msg2.txt | ham | 0.09 | confident-correct |
| part1/3-380msg1.txt | ham | 0.07 | confident-correct |
| part1/3-380msg4.txt | ham | 0.04 | confident-correct |
| part1/3-380msg5.txt | ham | 0.04 | confident-correct |
| part1/3-380msg6.txt | ham | 0.09 | confident-correct |
| part1/3-380msg7.txt | ham | 0.04 | confident-correct |
| part1/3-383msg1.txt | ham | 0.07 | confident-correct |
| part1/3-384msg2.txt | ham | 0.06 | confident-correct |
| part1/3-384msg3.txt | ham | 0.04 | confident-correct |
| part1/3-385msg1.txt | ham | 0.06 | confident-correct |
| part1/3-385msg3.txt | ham | 0.03 | confident-correct |
| part1/3-387msg0.txt | ham | 0.03 | confident-correct |
| part1/3-387msg2.txt | ham | 0.02 | confident-correct |
| part1/3-418msg3.txt | ham | 0.41 | confident-correct |
| part10/9-597msg2.txt | ham | 0.56 | wrong/near |
| part10/9-612msg2.txt | ham | 0.40 | confident-correct |
| part10/9-671msg1.txt | ham | 0.46 | confident-correct |
| part10/9-672msg1.txt | ham | 0.55 | wrong/near |
| part10/9-693msg1.txt | ham | 0.52 | wrong/near |
| part10/9-695msg1.txt | ham | 0.57 | wrong/near |
| part10/9-744msg1.txt | ham | 0.43 | confident-correct |
| part10/9-881msg1.txt | ham | 0.49 | confident-correct |
| part10/9-884msg1.txt | ham | 0.44 | confident-correct |
| part10/9-887msg1.txt | ham | 0.43 | confident-correct |
| part10/9-903msg1.txt | ham | 0.45 | confident-correct |
| part10/9-906msg1.txt | ham | 0.53 | wrong/near |
| part10/9-941msg1.txt | ham | 0.40 | confident-correct |
| part10/9-957msg1.txt | ham | 0.51 | wrong/near |
| part10/9-960msg1.txt | ham | 0.47 | confident-correct |
| part10/9-961msg1.txt | ham | 0.49 | confident-correct |
| part10/9-971msg1.txt | ham | 0.51 | wrong/near |
| part10/9-972msg1.txt | ham | 0.62 | wrong/near |
| part10/9-973msg1.txt | ham | 0.46 | confident-correct |

## Execution result

The differential was attempted against the ready local server with TYPESAFE_BASE_URL=http://127.0.0.1:8080 and TYPESAFE_API_KEY=local. The first attempt reached a request timeout; the extended-timeout retry reached this backend error:

502 upstream did not return an OpenAI chat completion: TypeError: message content is missing

The 40-case run produced no complete per-case agreement/delta vector. The LocalJev backend was live and the feasibility arm passed, but the workload was not stable enough to execute the preregistered denominator.

## Verdict

**BLOCKED** — not SUBSTITUTE or NOT-SUBSTITUTE. The failure is a LocalJev/oMLX backend completion error on the pinned differential workload, after the feasibility probe itself worked.

## No-claim

- No substitute verdict was issued.
- No agreement or probability-difference statistic was computed for the 40-case bar.
- Feasibility success does not establish calibration or workload-scale reliability.
- No LocalJev source or vendored clone was edited.

## P2-6 bounded retry (2026-09-19)

The pinned 40-case SHA and preregistered bar were not changed. The feasibility cases were rechecked first with the shared work/oracle-kit scorer:

- feasibility AUC: 1.0
- bar: 0.8
- constant score: false
- SDK field extraction used noul/probabilities and throws on missing fields

The 40 cases were then attempted with one question per LocalJev request, sequentially, with the SDK timeout raised to 180 seconds. This did not produce a complete vector. LocalJev returned:

    502 upstream did not return an OpenAI chat completion: TypeError: message content is missing

The bar remains unchanged. Verdict remains BLOCKED. This is a backend/model completion failure on the shrunk request, not a substitute/non-substitute result.

Exact served model: incoai/Qwen3.8-27B-Splash.

NO-CLAIM: feasibility correctness does not establish calibration; agreement with Jev would not establish accuracy because both systems can be wrong together.

## P2-7 state-length diagnosis (2026-09-19)

The exact long-state ladder used one pinned Ling-Spam email (full state 9,929 characters) and one noul question per call against the served model incoai/Qwen3.8-27B-Splash. Results:

| State chars | Result | p | wall ms | input tokens | output tokens |
|---:|---|---:|---:|---:|---:|
| 200 | OK | 0.10 | 4,356 | 343 | 173 |
| 1,000 | OK | 0.05 | 4,333 | 513 | 149 |
| 4,000 | OK | 0.03 | 4,850 | 1,164 | 129 |
| 9,929 | OK | 0.03 | 6,302 | 2,571 | 200 |

State length is not the threshold for this case. A direct oMLX request using the exact LocalJev chat payload for the 9,929-character state returned HTTP 200 with a nonempty message.content and a reasoning_content field. The raw response body is captured in the run evidence; it does not prove every model response has that shape.

The earlier LocalJev 502 remains a backend response-shape failure: message content missing. The direct representative long-state response does not reproduce it, so the cause is not diagnosed as a universal length ceiling or a universal reasoning-field parse bug.

Verdict: STILL-BLOCKED-WITH-RAW-BODY. The 40-case bar remains unchanged and no subset substitute verdict is claimed.

NO-CLAIM: no complete differential vector; agreement with Jev is not accuracy because both can be wrong together; finding is specific to incoai/Qwen3.8-27B-Splash and the observed LocalJev/oMLX response-shape failure.

## Direct oMLX body (representative long state)

This is the raw body from the direct upstream request for the 9,929-character case. It has message.content and finish_reason stop, plus reasoning_content; therefore it does not reproduce the LocalJev 502 on this representative input.

```json
{
  "id": "chatcmpl-39720ef7fddaa163fd9c69ef0d90666a",
  "object": "chat.completion",
  "created": 1789838156,
  "model": "incoai/Qwen3.8-27B-Splash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "\n\n{\"answers\":{\"q1\":0.03}}",
        "reasoning_content": "We need answer user's request. Need produce JSON only. Need classify q1 yes/no: Is this email spam? Document is an email invitation to become program committee member for GECCO-99. Need probability it is spam. We must evaluate only document. It appears legitimate academic conference solicitation, not spam. But could be mass email? It is targeted to recent authors, asks to email with info. Spam? likely no. Need calibrated probability. Maybe 0.05 or 0.1. Need return number. Since question yes/no: probability answer is yes. We need decide. The email is a conference invitation, likely not spam. But in spam classification datasets, this might be considered non-spam. It is a legitimate email from conference chair. Probability yes maybe 0.02. Need output JSON {\"answers\":{\"q1\":0.02}}. Ensure no markdown.\n"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 2571,
    "completion_tokens": 200,
    "total_tokens": 2771,
    "prompt_tokens_details": {
      "cached_tokens": 2560
    },
    "completion_tokens_details": {
      "reasoning_tokens": 186
    }
  },
  "metrics": {
    "prefill": {
      "tokens": 11
    },
    "decode": {
      "tokens": 192
    },
    "request_latency": {
      "start_to_first_token_ms": 660.157,
      "first_token_to_done_ms": 6028.001,
      "wall_ms": 6702.212,
      "ttft_ms": 674.2110000000002,
      "queue_to_start_ms": 14.054000000000201,
      "stream_tokens_per_second": 31.851355034612634
    },
    "cache": {
      "status": "hit",
      "matched_tokens": 2560,
      "capacity": 262144,
      "slot": 0
    }
  }
}
```
