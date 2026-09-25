# Skill routing for live units (pane 1, 2026-09-25)

Joshua, 2026-09-25, verbatim: "search for and install a library of relevant skills that give us
superpowers" / "lean on libraries with a lot of stars and heavy implmeentation rigor" / "keep going
on skills and make sure we're using them".

## What was installed

32 skills from four libraries, copied at pinned SHAs into `~/.claude/skills/` (`~/.agents/skills`
is a symlink to it). Provenance, license, ripwire scan verdict and SKILL.md hash per skill:
`~/.claude/skills/THIRD-PARTY-SKILLS.tsv`.

| Library | Stars | License | SHA | Skills |
|---|---|---|---|---|
| obra/superpowers | 291,300 | MIT | 5bf4e7801107 | systematic-debugging, verification-before-completion, brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, receiving-code-review, requesting-code-review, test-driven-development, writing-skills |
| K-Dense-AI/scientific-agent-skills | 46,579 | MIT | 49c6e97775ea | statistical-power, experimental-design, hypothesis-generation, scientific-critical-thinking, peer-review, statsmodels, scikit-learn, pymc, shap, stable-baselines3, pufferlib, pytorch-lightning, exploratory-data-analysis, networkx, polars, matplotlib |
| huggingface/skills | 11,097 | Apache-2.0 | 80f9fa530e46 | hf-cli, huggingface-datasets, huggingface-trackio |
| anthropics/skills | 178,019 | Apache-2.0 (per skill) | 33375500bcea | webapp-testing, skill-creator |

Left out on purpose: superpowers `using-git-worktrees` and `finishing-a-development-branch`
(AGENTS.md: main only, no worktrees), K-Dense `statistical-analysis` (name taken by an installed
skill), trailofbits/skills (security, not this lane's work). Scan: 0 CRITICAL; 13 K-Dense skills
WARN on `SCOPE-CREEP:bash-not-allowed`, a false positive (their `allowed-tools` lists Bash
space-separated). Bundled scripts grepped for network, exec and delete calls: the one `rm -rf` is
guarded to `/tmp/*`; the brainstorming server binds 127.0.0.1 with a token.

## Loading

A fresh omp session lists all 32 (`omp --profile claude --mode=rpc`, available commands,
2026-09-25). A session started before the install cannot resolve `skill://<name>` for them.
Until a pane restarts, packets give the file path: `/Users/josh/.claude/skills/<name>/SKILL.md`.
Subagents do not help: they inherit the parent session's skill list, so a subagent spawned from a
pane that started before the install also gets `Unknown skill` (SkillCensus and KeyExposure, both
2026-09-25). Give subagents the file path too, or restart the pane.

## Which skill for which unit

| Unit | Pane | Skills | What the skill decides |
|---|---|---|---|
| PokéJev `Unknown move: nothing` harness bug (84 + 105 fallbacks) | 3 | systematic-debugging, test-driven-development | root cause before fix; failing test first |
| PokéJev leaf evaluator dev arm (plan on jev-9gtw.1) | 3 | scikit-learn, statsmodels, shap, statistical-power | calibrated value model and its CIs, which state features drive it, battles needed for the bar |
| PokéJev obliterate target (>= 90% vs Abyssal) | 3 | statistical-power, huggingface-datasets, stable-baselines3 | 134 battles show a Wilson lower bound over 84% if the true rate is 90%; outcome-labelled replay data for a value model; offline-RL route if search tops out |
| PokéJev public watch mode (jev-jy7t.1.10) | any | webapp-testing | drive the Showdown challenge flow in a real browser |
| Jericho (Zork1, Detective, Deephome) | 2 | statistical-power, experimental-design | 3 seeds per arm has 6.5% power for the +5 bar; pair arms by seed and size the seed count before more runs |
| MiniWoB v3 per-arm isolation and combined held-out | 5 | experimental-design, statistical-power, systematic-debugging | one factor per arm; McNemar power on 625 episodes; the time-formatter bug |
| Emerald ROM build | 4 | systematic-debugging, verification-before-completion | build failures; sha1 match stated only from output |
| Non-author checks (every callback) | 1 | verification-before-completion, scientific-critical-thinking, peer-review | evidence before any closure |
| Skill-use census (jev-yy7f) | subagent | test-driven-development, verification-before-completion | fleet line shows which skills are actually read |

Every callback names the skill and the step or section that decided each choice. The skill-use
census line in the fleet check is how pane 1 checks that without asking.

## First use, measured

`statistical-power` (closed-form recipes, `statsmodels.stats.power`, run with
`uv run --with statsmodels --with scipy`), script `/tmp/power-jev.py`:

- PokéJev 70% bar at N=200: pass probability 0.535 if the true rate is 0.70, 0.955 at 0.75,
  0.000 at the measured 0.57. The bar is a sound kill rule.
- Jericho Zork1 with 3 seeds per arm and seed SD about 13 (scores 25, 44): power 0.065 for +5
  points, 0.29 for +20; minimum detectable difference at 80% power is about 41 points, more than
  Zork1 scores at the 35-step cap. As designed the bar can neither pass nor fail. Sent to pane 2
  before any Detective or Deephome run.
