# Q18 UBS provenance hold

Verdict: **UNASKABLE_PROVENANCE_HOLD**.

The build receipt claimed two critical UBS findings were false positives but did not include locations. I ran UBS three read-only ways over the exact four source files: JSON, SARIF, and verbose text. All returned the same aggregate 2-critical summary; none emitted per-critical file/line locations.

Source inspection found the likely non-security constructs, but cannot bind them to UBS critical #1 or #2:

- `run.mjs:48` reads `process.env.TYPESAFE_API_KEY`; this is environment wiring, not a secret comparison.
- `jev-client.mjs:17` builds the Authorization header; this is transport construction, not a comparison.
- `gate.mjs:66` validates the numeric Noul response with `typeof`; this is a typed-answer guard, not secret/signature/token comparison.

I therefore rule both criticals **UNASKABLE**, not FALSE_POSITIVE_CONFIRMED. The missing per-finding provenance is the finding.

Rerun cost: approximately 19 seconds for the three formats, read-only, with no key or network mutation. It was worth doing once because it established the output limitation. Repeating the same command is not worth it; a UBS scanner/module detail output or the absent scan log is required.

Retry condition: run the underlying scanner or UBS mode that emits file/line locations, then re-rule each critical independently.

NO-CLAIM: no source was changed, no UBS suppression was added, and no critical was declared false-positive.
