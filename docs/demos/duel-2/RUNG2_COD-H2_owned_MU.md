# Q14 ruling — does AutoModeMiddleware abstain? NO. COD-H2 survives narrowed.

Bead: `jev-demo-loop-a1q`. Unit Q14. Method: installed
`langchain-typesafe==0.0.1a2` from PyPI (no key, $0) and read
`experimental/middleware/auto_mode.py` (255 lines) in full. Vercel fx
auto-mode claims in the survey were not independently reachable from
here (search throttled, no source path given) and are NOT ruled on —
this verdict covers the LangChain artifact only.

## The control flow, quoted

`wrap_tool_call` (`auto_mode.py:220-226`, identical in `awrap_tool_call`
at 246-252):

```python
if request.tool_call["name"] not in self._tool_names:
    return handler(request)
response = self.classifier.invoke(self._classification_state(request))
probability = response.nouls[_QUESTION_ID].noul
if probability >= _PROBABILITY_THRESHOLD:
    return self._blocked_tool_message(request, probability)
return handler(request)
```

with `_PROBABILITY_THRESHOLD = 0.5` (line 39). The docstring states the
design in plain words (lines 75-88): *"Calls below `threshold` execute
normally. Calls at or above the threshold return an error `ToolMessage`
without invoking the tool handler"* and, dispositive: *"This middleware
blocks risky calls; **it does not request human approval**."*

The outcome space is exactly two: allow (handler runs) or deny (error
`ToolMessage`, `status="error"`, templated text with the probability).
There is no third path. No `clarify`, no `gather`, no `abstain`, no
`escalate`, no withhold-on-uncertainty, no confidence band, no human
routing of any kind. Classification failures propagate with the handler
unsent (fail-closed on error — sound, but failure ≠ abstention: it is
an exception path, not a verdict).

## The vendor-guidance check: not implemented

Survey-reported guidance: treat ~0.3–0.5 as a signal to ask a human
rather than act. The artifact has a single constant threshold at 0.5
and no band semantics anywhere in 255 lines — no 0.3 floor, no
"ask human" branch, no configurable policy map. A 0.49 call executes
silently; a 0.51 call errors. Stated plainly as ordered: the guidance
is not implemented. (Whether the guidance exists as stated is itself
unverified here — no source was given for it — but *if* it exists,
this code does not follow it.)

## Ruling: COD-H2 SURVIVES, narrowed to exactly the wedge

§3i does not kill here because the incumbent, though Jev-powered, does
not occupy COD-H2's distinctive claim. Abstention — declining with a
calibrated confidence through pass/clarify/gather/abstain/escalate/
block plus a withhold path — appears nowhere in the shipped control
flow. What ships is binary allow/deny at a fixed 0.5 with fail-closed
errors. COD-H2's surviving wedge, stated narrowly so it cannot drift:

1. a **withhold outcome** distinct from both allow and error-block
   (uncertain evidence must route somewhere other than execution or
   refusal);
2. **calibrated confidence with coverage semantics** (selective
   accuracy at stated coverage, not a point threshold);
3. at minimum a **human-routing outcome** (`clarify`/`escalate`) —
   the exact path the incumbent's docstring disavows.

Anything COD-H2 builds outside those three overlaps a shipped,
maintained artifact and should be cut on sight. Inside them, no
incumbent surveyed (including this one) competes.

## What the incumbent has that H2 must respect

Quoted to keep the wedge honest: 30-message state window with
assistant/tool context (`_classification_state`, lines 166-179);
per-tool scoping with pass-through for unlisted tools (line 220-221 —
narrower blast radius than a universal gate); trace redaction
(`TracePolicy(process_inputs=omit_payload)`, line 129 — they thought
about secret exposure in telemetry, which is more than most Jev
wrappers do); explicit experimental status with API-change warning.
H2's contract should adopt the redaction posture and the per-tool
scoping rather than re-learning them. Also noted: package version
**0.0.1a2** (alpha, experimental module) — shipped but young, API
explicitly unstable.

## NO-CLAIM

Source read, not run: no middleware instantiated, no tool call
classified, no LangChain agent constructed (would need peer deps
beyond the fetched package). Vercel fx claims untouched for lack of
a reachable source. The `0.3–0.5` guidance is checked against code
that contains no such band; the guidance's own provenance was not
verified. Verdict concerns the shipped control flow only.
