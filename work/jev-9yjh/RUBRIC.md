# STRICT usage rubric for memory keep labels (jev-9yjh, committed BEFORE labelling)

Question: was this kept memory actually USED by the turn, not merely topical?

## Labels

**RELEVANT** iff the session's subsequent answer or actions demonstrably use the
memory's content, verified against the session transcript:
- the assistant quotes, cites, or names a fact from the memory; or
- a tool call acts on an entity/number/path taken from the memory; or
- the turn visibly continues a task the memory describes (same bead id, same
  named artifact, same quoted verdict) where the memory supplies necessary context.

**IRRELEVANT** otherwise, including:
- topical-but-unused (same project/bead, no demonstrable use);
- product instruction prose (memory-system instructions, precedence notes);
- fragments, echoes, tag literals, status lines that changed nothing;
- memories about a different task, even in the same repo;
- content-free truncations.

## Anchors

- RELEVANT: prompt "Summarize the rud1 WITHHOLD verdict and its numbers" +
  memory stating the rud1 verdict with catch 26/30, followed by an answer
  repeating those numbers.
- IRRELEVANT (topical): prompt about uds grades + memory "uds is the
  apply-half management plane ..." with the answer not using it.
- IRRELEVANT (prose): any prompt + "This agent has local Mnemopi ..." preamble.

## Protocol

- Labeller (HazySpring, second labeller; first = WindyLantern m959 labels) works
  from prompt+memory text with the author labels and nouls hidden.
- For each keep: locate the turn in session files by prompt text, read the
  subsequent assistant messages/tool calls, judge used/unused.
- Record per item: id, strict label, one-line evidence (quoted use or "no use
  found in N following messages").
- Then unblind: agreement rate + Cohen's kappa vs m959 labels; label-noise
  ceiling = best keep precision attainable given disagreement; re-score Jev
  keeps vs strict labels.
