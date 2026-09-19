# Report-only defects from P2 compaction install/run

**Target:** `upstream/tamaratran/fast-jev-compaction` at `6e1da50d`
**Status:** report-only; no upstream clone edits.

## 1. README has no real omp SessionEntry path

The README documents the package `Message` shape and Claude plugin install, but it does not explain
how to read an omp-written session JSONL file. Real omp files use `type: message` entries, whole
messages with `role: toolResult`, `toolCallId`, and content that may be a bare string; they do not
use the stream `message_end` event shape consumed by the local adapter.

A stranger following only the upstream README cannot take a real `~/.omp/profiles/.../sessions/*.jsonl`
file and run the package against it. P2 used a separate adapter in a clean workdir to bridge this
shape.

Suggested upstream fix: document the accepted on-disk schema or ship a SessionEntry adapter, with a
real-file example and a known-bad shape test. No patch submitted.

## 2. Real large histories fail at the state ceiling without a documented preflight path

The richest available real session had 11,824 tool results and roughly 370,635 estimated tokens
after the library's truncation stages. The upstream compactor refused before making a request:

```text
history too large for Jev (~370635 tokens after truncation, limit 25000)
```

The README describes the fitting stages but does not provide a caller-visible preflight command,
chunking policy, or clear handling guidance for a real history that cannot fit. The library does
throw as documented, so this is a usability/operational gap rather than a silent correctness bug.

Suggested upstream fix: expose a preflight result with estimated size and required action, or
provide a documented adapter policy for splitting/deferring oversized real histories. No patch
submitted.

## No-claims

- The package's 29 tests, typecheck, and build pass.
- A smaller real session compacted successfully: 48,062 serialized bytes to 889, one request,
  351 ms compactor time, and $0.000126462 under the stated input rate.
- The live result proves byte/token reduction only, not task continuation quality.
