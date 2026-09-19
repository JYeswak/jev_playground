# `jev-0c6` — real SessionEntry adapter boundary

**Real input:** `~/.omp/profiles/omp-3/agent/sessions/-Developer-control-plane/2026-08-21T18-59-18-098Z_01a025b1-17b7-72f0-b68a-96bb37379e3f.jsonl`

Observed file shape:

```text
136K, 43 rows
message: 24
custom: 15
message_end: 0
```

The current adapter reads only `message_end` stream events. Running the real file through the
upstream replay path with a live Jev key produced:

```text
PASS output texts are verbatim input subsequence
PASS every non-blank input text survives
PASS no invented ids; results exact or truncated
PASS vanished messages carried no text
PASS candidates imply requests
FAIL library saw tool calls
exit=1
```

The replay receipt was written outside the repository at `/tmp/jev-0c6-real-replay.json`. No
successful compaction or false green is claimed. The acceptance boundary is currently unobtainable
without implementing the second `SessionEntry`/`type: message` adapter shape; the existing stream
path remains untouched.
