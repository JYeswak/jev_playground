#!/usr/bin/env python3
"""Gap funnel for .rs threads: signal -> occurrences -> bind.

PREREGISTERED SIGNALS (gap in the payload, not topic of the file):
  UNSAFE:   .rs edit/write payload contains whole-word `unsafe`.
  ERROR:    payload matches new-error-type shape:
            (enum|struct) <Name>Error | derive listing Error | #[error | type Error =
  NEWTYPE:  payload matches tuple-struct shape or PhantomData:
            struct Name( [with optional pub] | PhantomData
  ORACLE:   path contains an oracle-domain token (sqlite|redis|http|quic|
            graph|dataframe|ndarray|markdown|terminal|libc|diar|raptor|
            numpy|scipy|telnyx|metal|video|sms). TOPIC-ONLY by construction:
            expected stage-1 FAIL (no gap visibility in a path); the count
            quantifies what a topic trigger would spam.
PREREGISTERED BARS: occurrences >= 50 to earn a bind sample; bind sample =
  20 rows uniform without replacement, seed 20260920, hand-labelled by me;
  survivor needs bind >= 20%. Else the thread is REFUSED (no signal /
  too rare / low bind) or UNDELIVERABLE-AS-RULE (oracle: gap invisible).
  parking_lot excluded here: Category A, builtin fires already.
FUNNEL REPORT: threads in (4) -> with detectable signal -> clearing 50 ->
  clearing 20% bind. Expect zero or one survivor; a refusal closes the
  thread permanently, by design.
NO-CLAIM: payloads are full write contents but patch fragments for edit
  calls; ADDS-vs-touches is not distinguished. Concentration quoted.
"""

import json
import os
import random
import re
from collections import Counter
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
SEED = 20260920
N_LABEL = 20
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gap-funnel-20260920.json")

ERROR_RX = re.compile(
    r"(enum|struct)\s+\w*Error\b|derive\([^)]*\bError\b|#\[error\b|type\s+Error\s*="
)
NEWTYPE_RX = re.compile(r"struct\s+\w+\s*\(\s*(pub\s+)?\w|PhantomData")
UNSAFE_RX = re.compile(r"(?<![a-z0-9_])unsafe(?![a-z0-9_])")
ORACLE_TOKENS = (
    "sqlite",
    "redis",
    "http",
    "quic",
    "graph",
    "dataframe",
    "ndarray",
    "markdown",
    "terminal",
    "libc",
    "diar",
    "raptor",
    "numpy",
    "scipy",
    "telnyx",
    "metal",
    "video",
    "sms",
)

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)} ts={ts}")

rs_calls = 0
hits = {t: [] for t in ("unsafe", "error", "newtype", "oracle")}
sessions = {t: set() for t in hits}

for fp in sorted(files):
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message") or {}
                if msg.get("role") != "assistant":
                    continue
                for c in msg.get("content") or []:
                    if not isinstance(c, dict) or c.get("type") != "toolCall":
                        continue
                    if str(c.get("name") or "").lower() not in ("edit", "write"):
                        continue
                    args = c.get("arguments") or {}
                    path = args.get("path") or args.get("file") or ""
                    if not isinstance(path, str) or not path.endswith(".rs"):
                        continue
                    rs_calls += 1
                    blob = json.dumps(args, sort_keys=True)
                    base = os.path.basename(fp)
                    if UNSAFE_RX.search(blob):
                        hits["unsafe"].append((base, path[:160], blob[:2000]))
                        sessions["unsafe"].add(base)
                    if ERROR_RX.search(blob):
                        hits["error"].append((base, path[:160], blob[:2000]))
                        sessions["error"].add(base)
                    if NEWTYPE_RX.search(blob):
                        hits["newtype"].append((base, path[:160], blob[:2000]))
                        sessions["newtype"].add(base)
                    low = path.lower()
                    if any(tok in low for tok in ORACLE_TOKENS):
                        hits["oracle"].append((base, path[:160], blob[:2000]))
                        sessions["oracle"].add(base)
    except OSError:
        continue

print(f"rs_edit_write_calls={rs_calls}")
rng = random.Random(SEED)
report = {
    "ts": ts,
    "corpus_files": len(files),
    "rs_calls": rs_calls,
    "seed": SEED,
    "threads": {},
}
for t in ("unsafe", "error", "newtype", "oracle"):
    n = len(hits[t])
    rate = n / rs_calls * 100 if rs_calls else 0.0
    top_share = 0.0
    if hits[t]:
        per = Counter(s for s, _p, _b in hits[t])
        top_share = per.most_common(1)[0][1] / n
    sample = rng.sample(hits[t], min(N_LABEL, n)) if n else []
    report["threads"][t] = {
        "occurrences": n,
        "rate_pct_of_rs_calls": round(rate, 4),
        "sessions": len(sessions[t]),
        "top_session_share": round(top_share, 4),
        "label_sample": [{"session": s, "path": p, "excerpt": b} for s, p, b in sample],
    }
    print(
        f"{t}: occurrences={n} rate={rate:.4f}% sessions={len(sessions[t])} "
        f"top_share={top_share:.3f} sample={len(sample)}"
    )

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, sort_keys=True)
print(f"out={OUT}")
