# Q49 — evidence-carrying manifest specification

Status: schema and price design.
Purpose: make each Q37 label re-derivable from committed evidence without access to mutable journal
files.
Constraint: the current journal files are absent; the 24-case prototype below is a lower-bound
price, not a completed exact-span conversion.

## Failure being fixed

The current 68-case manifest carries journal path/SHA, turn index, command SHA, and a scrubbed
160-character preview. Later verification found 40/68 previews unable to evidence their own stratum
labels and four cases no longer relocatable because live journals changed. Coordinates into a mutable
journal are not evidence. A third party cannot confirm a label from the manifest alone.

The replacement carries the evidence bytes used for the label, plus provenance proving where those
bytes came from when the source snapshot exists.

## Per-case schema

```json
{
  "case_id": "<journal>:<turn_index>",
  "stratum": "reversible_safe | disallowed_destructive | ambiguous_authority | credential_injection",
  "band_member": false,
  "source": {
    "journal_path": "-Developer-...jsonl",
    "journal_sha256": "...",
    "turn_index": 37,
    "source_snapshot_sha256": "...",
    "source_available_at_build": true
  },
  "turn": {
    "event_index": 123,
    "start_byte": 987654,
    "end_byte": 988432,
    "raw_turn_sha256": "..."
  },
  "command": {
    "text": "rm -- /tmp/example && ls ...",
    "encoding": "utf-8",
    "bytes_b64": "...",
    "sha256": "...",
    "start_byte": 988010,
    "end_byte": 988084
  },
  "context_spans": [
    {
      "role": "user|assistant|tool_result",
      "text": "...",
      "bytes_b64": "...",
      "sha256": "...",
      "start_byte": 986100,
      "end_byte": 986260,
      "source_turn_index": 36
    }
  ],
  "policy": {
    "label": "pass | withhold | escalate | block",
    "policy_sha256": "policy.json hash",
    "policy_paths": ["/question/criteria_false", "/mapping/withhold_band"],
    "rubric_version": "L-AUTH-01..L-BLOCK-01"
  },
  "redaction": {
    "applied": false,
    "patterns": [],
    "raw_secret_bytes_in_manifest": false
  }
}
```

### Boundary requirements

- All byte ranges are half-open UTF-8 offsets into the immutable source snapshot.
- `bytes_b64` is the evidence used by the label; `text` is a readable rendering and is not the
  integrity authority.
- Every span carries its own SHA-256 and the parent turn carries a raw-turn SHA-256.
- The manifest stores scrubbed evidence only. If a value is secret-shaped, the case is redacted or
  synthetic; the original secret is never embedded.
- Context spans include enough preceding/following evidence to decide authority and scope, not merely
  the command line. The exact window rule is committed before conversion.
- `source_snapshot_sha256` is provenance, not a dependency for verification. A third party can verify
  the label from `bytes_b64`, hashes, policy paths, and rubric version alone.
- A missing byte range or missing evidence span is `UNASKABLE`, not an inferred pass/withhold.
- The manifest is append-only and content-addressed. A new source snapshot creates a new manifest;
  it never rewrites the old one.

## Label verification from manifest alone

A verifier needs no journal access:

1. Parse JSON and verify manifest/schema version.
2. Decode every `bytes_b64` value and recompute its SHA-256.
3. Verify each turn hash from its included raw turn/spans.
4. Confirm the command bytes are included in the turn evidence and match the command hash.
5. Verify the policy hash and each cited JSON path against the pinned policy/rubric version.
6. Re-run the deterministic pattern rules over the included command bytes.
7. Confirm the recorded label is permitted by the cited policy clause and evidence availability.
8. Reject duplicate case IDs, missing spans, hash mismatches, unknown policy paths, and labels whose
   source evidence is absent.

This verifies the **label artifact**, not whether the human rubric itself is philosophically correct.
That distinction remains explicit.

## 24-case conversion price

The available manifest has 68 cases, but the source journals are absent from the checkout. The
measured prototype converted 24 available records—8 reversible, 4 disallowed, 12 ambiguous—using the
scrubbed preview as a lower-bound evidence span and recording `source_available=false` and null byte
ranges. It deliberately did not invent source offsets.

Measured command: deterministic Python conversion over the committed corpus and labels. Results:

| Measurement | Value |
|---|---:|
| Prototype cases | 24 |
| Raw selected-case JSON | 13,154 bytes |
| Evidence-manifest prototype | 25,521 bytes |
| Inline preview bytes | 3,272 bytes |
| Metadata/hash/provenance overhead | 22,249 bytes |
| Prototype bytes per case | 1,063.4 |
| Measured conversion runtime | 0.000185 seconds |

The runtime is not human labeling time; it prices serialization only. The prototype is a lower bound
because it lacks full turn/context spans. Extrapolation at the observed per-case size:

- 68 cases: approximately **72,310 bytes**;
- 200 cases: approximately **212,675 bytes**;
- additional full context spans, base64 expansion, and immutable source snapshots will increase those
  values.

A practical upper budget should reserve 1–4 KB per case depending on context window. That yields
approximately 68–272 KB for 68 cases and 200–800 KB for 200 cases, still practical for a committed
receipt bundle but large enough to justify compression and chunked evidence files. The verifier must
hash chunks and retain the manifest's content-addressed references; compression must not remove
verifiable decoded bytes.

## What must happen before exact conversion

The 24-case prototype cannot be promoted to the exact manifest because its source journal files are
absent. The next run needs one of:

1. the immutable journal snapshot used by the draw, mounted read-only;
2. a content-addressed archive containing the 24/68 source turns; or
3. a new draw from a present immutable corpus, with new seed and labels.

Do not fill missing spans from memory, previews, or current live journals. That would recreate the
same drift defect Q44 found. If only the 24 verifiable cases can be reconstructed, label that set and
state that it is not a 68/200 sample.

## Q49 decision

**The evidence-carrying manifest is practical in size, but exact conversion is currently BLOCKED by
missing source snapshots.** The schema is worth implementing after the snapshot arrives. It converts
“trust this journal coordinate” into “verify these committed bytes,” and it makes the policy clause
and evidence available to the blind auditor.

## NO-CLAIM

No labels were changed, no source journal was recovered, no secret was handled, and no model call was
made. The 24-case byte price is a lower-bound serialization measurement over previews, not a completed
full-span manifest or a claim that the 68-case corpus is independently verifiable today.
