# Synthesis: next-gen Jev for computer use and games (beads `jev-jy7t`, `jev-jy7t.1`)

Pane 1 (AmberWillow, orchestrator), 2026-09-24. Two wizards, one brief, adversarial cross-scoring:
Claude (pane 3, SapphireFalcon, Opus 5.5) and Codex (pane 4, WindyLantern, GPT-5.6-Luna). Pane 1
generated no ideas and scored none; sections 1-4 report the wizards' own numbers and arguments.
Pane 1's own view is confined to sections 5 and 6.

Joshua's directives, verbatim: *"i want a cluster of truly novel ideas that jev can be used for -
computer use, game use, with examples that we run locally - anything we can come up with that is
truly novel in its approach - must shatter any sota approaches we find."* / *"do deep online research
to back this up - what are people using classifier models like jev for"* / *"make sure that this
exercise is backed with latest research and guidance"*.

## Artifacts (all on `main`)

| Phase | Files |
|---|---|
| Brief | [`BRIEF.md`](BRIEF.md) (sections 9-10 carry the focus change and omp 18.3) |
| Research | [`research-classifier-uses.md`](research-classifier-uses.md), [`research-sota.md`](research-sota.md), [`research-guidance.md`](research-guidance.md), [`local-env-probe.md`](local-env-probe.md), [`ledger-20260924.md`](ledger-20260924.md), [`outside-scan-20260924.md`](outside-scan-20260924.md) |
| Ideas (30 each) | [`WIZARD_IDEAS_CC.md`](WIZARD_IDEAS_CC.md) `13a0559`, [`WIZARD_IDEAS_COD.md`](WIZARD_IDEAS_COD.md) `5c065f5` |
| Cross-scores | [`WIZARD_SCORES_CC_ON_COD.md`](WIZARD_SCORES_CC_ON_COD.md) `271eff3`, [`WIZARD_SCORES_COD_ON_CC.md`](WIZARD_SCORES_COD_ON_CC.md) `ab8cd16` |
| Reactions + blind spots | [`WIZARD_REACTIONS_CC.md`](WIZARD_REACTIONS_CC.md) `0353995`, [`WIZARD_REACTIONS_COD.md`](WIZARD_REACTIONS_COD.md) `0ef1ef0` |

## 1. Score matrix

Scores are 0-1000. "Other" is the opposing wizard's score; "Self" is the author's score after the
reveal.

| Idea | Author | Other | Self (revised) | Verdict |
|---|---|---:|---:|---|
| **PokéJev:** Jev in PokéChamp's three LLM slots, clock-proof expectiminimax on Pokémon Showdown | CC | 790 | 780 | **Consensus winner** |
| **Jev-PUCT:** MC-DML's log-prob prior replaced by a Jev Choice, Jericho text adventures | CC | 705 | 740 | **Consensus winner** |
| MiniWoB++ DOM action lattice (Choice over code-enumerated element/operation pairs) | COD | 540 | 650 | Contested; merges with CC's verifier slot |
| V-Droid verifier slot, training-free (now MiniWoB-first) | CC | 660 | 520 | Contested; merges with the DOM lattice |
| Certified step monitor (Jev Nouls into CUSUM) on released OSWorld trajectories | CC | 610 | 620 | Middle; parked |
| BrowseSafe injection shield | CC | 555 | 560 | Middle; parked |
| Web Step Surgeon (transition verifier), rebased onto static judge sets | COD | 340 | 545 | Contested; parked |
| ReflexGate on the Real-Time Reasoning Gym | COD | 380 | 410 | Weak: latency demo only |
| BALROG relative-comparison tree search (Crafter/TextWorld subset) | COD | 360 | 385 | Weak |
| ViZDoom symbolic real-time controller | COD | 300 | 240 | **Killed** (both agree a scripted floor wins) |

**Blind spots** (proposed after the exchange; not cross-scored):

| Idea | Author | Self | Note |
|---|---|---:|---|
| **Best-of-N selection:** one Jev Choice picks the winning trajectory among N released OSWorld-Verified runs per task; the official `result.txt` grades the pick | CC | (none given) | Ground truth exists today; about $0.4 |
| **AX-tree pruning:** Jev Nouls prune a live accessibility tree before a planner sees it | COD | 735 | MiniWoB first, native Mac apps second |

## 2. Where the wizards converged

1. **The mechanism that makes these ideas new.** The strongest published LLM search recipes need
   per-option likelihoods that frontier APIs no longer expose: MC-DML's prior comes from
   `gpt-3.5-turbo-0125` top-20 log-probs (arXiv 2504.16855), V-Droid scores candidates by prefill
   (2503.15937), and KnowNo needs per-option likelihoods. Jev returns a calibrated distribution over
   up to 255 options as its native output, in about 130 ms. Both consensus winners and the Best-of-N
   blind spot put exactly that distribution where an LLM log-prob or an LLM judge used to be.
2. **The clock, not knowledge, is where LLM agents lose.** Checked at the source by pane 1:
   PokéChamp's ladder paragraph (2503.04094) says *"For about one third of the games, PokéChamp lost
   by exceeding the turn time limit. Within the remaining two thirds of games, PokéChamp achieved a
   76% win rate."* Its Gen 9 OU clock is 150 s per game plus 15 s per turn.
3. **The scripted-floor trap.** Where the state is symbolic and real-time (Freeway, Snake, Defend the
   Center, StarCraft II vs the built-in AI, 2048, Tetris, Sokoban), a scripted bot with zero model
   calls beats every LLM row. There, only an "LLM-agent row" could fall, never overall SOTA. Codex
   conceded this for ReflexGate, BALROG and ViZDoom; ViZDoom is killed.
4. **Protocol before numbers.** Every browser SOTA number needs its exact observation type, task
   split and evaluator. Claude caught that BrowserGym's MiniWoB split is 125 tasks, not 46, and that
   OrbyAgent's 74.9 also reads screenshots. Codex caught that one of Claude's data sources had no
   per-step records.

## 3. Where they still disagree

- **Cost framing.** Codex wanted smaller first runs to save money; Claude cited AGENTS.md's lifted
  budget gate and MC-DML's Algorithm 1 (one prior per expanded node, not ten times that). The budget
  gate is lifted for Jev calls; the like-for-like simulation budget stands.
- **Speculator vs PUCT.** Codex would merge them; Claude keeps them apart (different ground truth).
- **Game-QA vs CUSUM.** Partly merged: shared alarm machinery, separate ground truth (HackAtari's
  injected bugs).

## 4. Measurements made during the duel (keyless)

| What | Command owner | Result |
|---|---|---|
| Jericho on arm64 Docker | CC | `jericho 3.3.1`; Zork1 and all 9 MC-DML games load; save/restore replays identically; 7 ms per restore + step + valid actions |
| Pokémon Showdown + poke-env locally | CC | 10 battles in 13.4 s; heuristic 10 wins vs random 0 |
| OSWorld-Verified released runs | CC | 60+ runs × 361 tasks with `traj.jsonl`, `runtime.log`, `result.txt`; `claude-4-sonnet-20250514-15steps` is 110/361; a range reader fetches one trajectory from a 3.56 GB zip after 2.1 MB |
| 15 environments on this Mac | LocalEnvProbe | [`local-env-probe.md`](local-env-probe.md) |

## 5. Pane 1's checks and additions

- **The PokéJev bar is against the LLM rows, not overall SOTA.** The strongest Pokémon battler is not
  an LLM agent: Metamon, offline RL with transformers (RLC 2025, arXiv 2504.04395), was the winning
  baseline of the NeurIPS 2025 PokéAgent Challenge (arXiv 2603.15563, Mar 2026) and, per its README,
  rates in the 90th-99th percentile against human players depending on the ruleset. So "shatter"
  for PokéJev is stated in two tiers: (1) beat PokéChamp-GPT-4o's published 84% against Abyssal with
  zero losses on time; (2) stretch, win against a released Metamon checkpoint on the local server.
  Only (2) would be a claim against the best agent of any kind.
- **Public-ladder play is Joshua's call.** Stage C of PokéJev plays on a public server against other
  players. That is an external action; it waits for Joshua's explicit go. Stages A and B are local.
- **Selection by the lane's rules** (ground truth exists today, prevalence, cost to measure,
  decision leverage):

| Rank | Idea | Ground truth today | Cost to first result | Leverage |
|---:|---|---|---|---|
| 1 | Best-of-N over released OSWorld runs | yes: official `result.txt`, on Hugging Face | about $0.4, offline data step keyless | high: the same selector can pick among N omp subagent attempts |
| 2 | PokéJev | yes: local battle outcomes; replay files for the Stage A gate | Stage A about $0.13; Stage B about $30 | game demo; clock-proof search is the novel claim |
| 3 | Jev-PUCT on Jericho | yes: game score, 9 published games | about $21 for 9 runs | text-game search without log-probs |
| 4 | MiniWoB lattice + verifier slot (merged) | yes: task checker | cents | browser; also needs pane 2's floors |
| 5 | AX-tree pruning | yes: task checker | cents | native Mac, and omp's own `computer` AX trees |

## 6. Next steps (beads under `jev-jy7t.1`)

1. **Best-of-N over released OSWorld runs:** keyless first (oracle@N and best single run from
   `result.txt`), then the preregistered Choice. Built by a non-author (pane 4).
2. **PokéJev:** Stage A gate (replay prediction), then Stage B local battles against Abyssal and the
   poke-env heuristics, then the Metamon stretch. Built by its author (pane 3); checked by a
   non-author.
3. **Jev-PUCT on Jericho:** after pane 2's floors unit (`jev-jy7t.1.1`).
4. **MiniWoB lattice + verifier slot** and **AX-tree pruning:** filed at lower priority; they reuse
   pane 2's MiniWoB floor.
5. **Parked, not filed:** certified step monitor, BrowseSafe shield, Web Step Surgeon, ReflexGate,
   BALROG subset. Their cases are in the wizard files; any one of them can be filed if a winner
   above dies.

Honest outcome words only, per the brief: BEAT, TIE, LOSE, NOT-SCORED. No result here is a ruling,
and every bar is preregistered before the first live call.
