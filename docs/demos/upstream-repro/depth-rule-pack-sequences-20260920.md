# Sequence mining (read-bursts, skill-routing): prereg receipt `[test]`

P1 STOP-D5 order: D5 refused by P4 (6480170, concentration + labels). Open and unmeasured:
toolCall SEQUENCES over the session-JSONL toolCall corpus (my walk 2026-09-20: 1,825 files,
416,570 toolCalls — quote both with timestamp; corpus drifts as sessions write).

Corpus shape verified this pass: top names eval 227,488 / bash 86,394 / todo 26,691 /
read 26,189 / write 15,003 / edit 14,947 / hub 9,565 / grep 5,838 / glob 1,096 /
task 314. No morph/ripwire MCP tool names (both run via bash; socraticode 2).
read args `{i, path}`, bash args `{command, i}` — paths and commands observable per call,
file order chronological. Mining is read-only.

## Preregistered bars (written BEFORE measuring, 2026-09-20)

- Wallpaper: firing windows above ~5% of sessions; too rare: below 50 session-windows.
- Hand-label seeded n≥20 WITH window context; ship-bar strict-FP ≤0.35.
- **Concentration check (new standing method):** report share of hits from the top session;
  a class carried by one session is a habit, not a rule.
- **TTSR-expressibility gate (separate from prevalence):** TTSR conditions match ONE tool
  call or text stream — a multi-call window is not expressible as a rule. Mining answers
  "does the habit exist"; a second ruling decides shippability (per-call proxy or NO-GO
  with the reason). Do not imply a rule from a rate.

## D4 read-burst (preregistered predicate)

Window: ≥5 `read` calls within any 10-consecutive-call window, majority same directory,
AND no deep-tool contact (bash command containing `ripwire|morph|ast-grep|\bsg\b|socraticode`,
or a `grep`-tool structural call — literal, counted separately) in the 10 calls before
window start. K=5, window=10, lookback=10 fixed before measuring; no tuning to data.

## D6 skill-routing (measurability probe first)

"Task names a domain we own a skill for, skill never read." Observable proxies: `read`
calls with `SKILL` in path (count first); `task`-tool prompts naming domains (314 calls).
If skill consultation is system-prompt-invisible, the class REFUSES as unmeasurable with
the evidence (counts), not a rate. No rate manufactured.


## Results (2026-09-20, files=1826, walks at 21:25–21:28Z — denominator drifts, quoted)

### D4 read-burst: three strikes, class REFUSED for TTSR

| pred | shape | bursts | top1 | labels (STRICT, own seeds) | verdict |
|---|---|---:|---|---|---|
| v1 | ≥5 reads/10-call window, same dir, no deep in prior 10 | 920 merged | 8.5% ✓ | 5/20 TP, FP 0.75 (seed 20260924) | REFUSE: mostly ranged evidence-gathering at known spots |
| v2 | v1 + whole-file only + pos<0.35 + no skill: reads | 75 | 2.7% ✓ | 10/20 TP, FP 0.50 (seed 20260925) | REFUSE: FP drivers are mandated-correct reads (AGENTS.md-first, docs, own .out/.err, re-reads) — a rule would punish doctrine |
| v3 | v2 + code extensions only | 13 | 7.7% | — (below floor, no labels burned) | REFUSE: n<50 |

FP driver, stable across versions: a ranged read (`file:line`) implies a KNOWN location =
navigation, the same named-vs-shape split that decided the grep rule. Cold-map cases are real
(pos≤0.28 whole-file dir surveys) but rare. TTSR-expressibility NO-GO independently: a
multi-call window is not a per-call condition, so even v3 could not ship as a rule — prevalence
finding only. Handoff, not a build: session-start doctrine already says ripwire-first; a
counter would belong to RECALL/hook surfaces, which are P4-dead and P1-dogfood respectively.

### D6 skill-routing: MEASURABLE, not a TTSR build — handoff with numbers

Skill consultation is observable: 1,267 `read` calls with `skill:`/`SKILL` in path across
206/1826 sessions (11%). Top: `skill://agent-mail` 46, `beads-north-star` 45,
`using-superpowers` 42, `zeststream-rch` 39. Prereg "system-prompt-invisible" fear REFUTED —
agents actively pull skills via reads. But the TTSR shape ("fire on domain X without skill-X
read") needs per-session read-history no stateless condition can see; as pure ROUTING it is
651 domain rules, which is P2's retrieval build (sr dead, Quill fallback per 984b501), not a
P3 predicate. Numbers handed off; no TTSR rule from this class by me.

## NO-CLAIM

Walks are mine (seeds 20260924/25/26); labels mine except where noted. All rates carry
files+N+timestamp above. Window predicates are corpus-specific tunables (K/W/LB/POS preregistered,
v2/v3 deltas principled: range-implies-known-location, ripwire-maps-code-not-prose) — a second
labeller re-running `/tmp/d4mine*.py` seeds moves the FPs, not the rarity wall (v3 n=13).
