# Q15 ruling — COD-H5 vs shipped fast-jev-compaction: DIFFERENT PRODUCTS

Bead: `jev-demo-loop-a1q`. Unit Q15. Method: read
`github.com/tamaratran/fast-jev-compaction` (903 stars, 39 forks, MIT)
in full via API — README, file tree, options table, limitations,
plugin docs. No code executed, nothing installed. (Familiarity note:
this tree is upstream of our vendored `fast-jev-compaction@6e1da50` —
same `src/` modules, same `hooks/fast-jev.ts` — which I read line by
line during the hook bead. No new claims below depend on memory of
that read; all citations are to the fetched README.)

## What the shipped tool is

A relevance-pruning compactor, stated in its own first paragraph:
*"replaces the compaction summary with Jev decisions: every tool call
and result is scored in one fast request, stale ones are dropped or
truncated, everything kept stays verbatim."* Mechanism (their "How it
works" §1–7): pair uses with results, pin first/newest messages, fit
state into token stages, ask two `noul` questions per call (keep the
call? keep the result verbatim?), apply keep/drop/truncate by
threshold, rebuild the message list. Outputs: pruned messages,
`decisions`, `stats` (message/char counts, per-reason decision counts,
state tokens, fitting stage, request count).

## What it is not: integrity detection, anywhere

Searched the README end to end for the H5 vocabulary — *before/after
fact comparison, loss detection, provenance span, flush ordering,
retention recall, boundary regression, source range* — and found none
of it, because none of it is in the product:

1. **Direction in time is opposite.** The plugin decides *before* the
   cut (which calls survive). H5 measures *after* the cut (which facts
   survived). A keep/drop verdict is a forward relevance judgment, not
   a post-hoc loss detection against a fact set. Nothing in `stats`
   names a lost fact.
2. **No fact set exists.** H5's core object — a source-span fact set
   compared pre/post boundary with provenance completeness — has no
   counterpart: the plugin's state *omits* results by design (`ok,
   4213 chars (omitted)`), and its decisions carry no source ranges.
3. **No ordering semantics.** Flush-before-truncate, pending-buffer
   loss, duplicate retry, stale generation — H5's EVAL list — appear
   nowhere; the plugin has one compaction pass with concurrent
   requests, no lifecycle, no generations.
4. **Its own limitations confess the gap.** *"Calibration is at the
   request level; a probability is not a proof that a result is safe
   to delete."* A tool that cannot prove safe deletion is precisely a
   tool whose deletions need an independent integrity check. The
   limitation section is H5's charter, written by its own author.

## Ruling: DISTINCT — and tester-to-subject, not rivals

COD-H5 survives Q15 intact. Stronger than mere distinctness: H5 can
benchmark fast-jev-compaction itself. Our own A/B already ran that
experiment once (pruned context 1/3 recall vs summary 3/3) — an H5
harness would run it on every transcript, against every compaction
implementation including native ones. The shipped tool does not detect
what compaction destroyed; H5 detects exactly that, for any compactor
handed to it. Tester to subject is a complementary relationship, and
complementary is not overlapping.

## What would collapse the distinction

One observable would merge them: a shipped `integrity` mode in
fast-jev-compaction emitting pre/post fact retention against source
spans. Nothing in the fetched tree (options table ends at
`truncateHeadChars`; test files cover library + hook only) shows it.
If it lands, H5's wedge narrows to cross-implementation portability —
revisit then, not now.

## Untouched by this ruling

- Diogo Almeida's quoted reply ("free coding agents from designing
  around the KV cache"): survey-cited, not verified here — irrelevant
  to product distinction either way.
- "1M tokens to 86K in one second": performance claim, not read as a
  measurement here; the README documents concurrent requests but no
  benchmark. Likewise irrelevant to the distinction.
- Demand for H5 (rung-1 895): unchanged up or down. This unit rules
  product identity only.
- Stars (903) as adoption evidence: noted and set aside — popularity
  does not decide product boundaries, mechanism does.

## NO-CLAIM

Source read, never run or installed. No compaction executed, no facts
compared, no benchmark reproduced. The distinction above is textual
and architectural: the shipped README contains no integrity-detection
surface, and H5's specified surface (fact sets, provenance, ordering)
appears nowhere in it.
