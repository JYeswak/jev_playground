# Memory keep-precision ceiling: labels vs base rate vs model (jev-2zbl add-on, 2026-10-02)

Question: six keep designs (R137, R139, jev-9n6h, jev-28gx, jev-h1hr R146) cap keep
precision ~0.22-0.23 with drops 0.976-0.978. Where is the ceiling?

## Measurements (all keyless)

1. Blind re-label: 90 frozen pairs (50 m959 + 40 h28 heldout), rater blind to frozen
   labels. Agreement 79/90 = 0.878, kappa 0.411 (mine relevant 8 vs frozen 13, overlap 5).
   Assets: `var/agent-tmp/dr4p-feas.34880/mem_blind.json`.
2. Downstream use: 2 model-kept organic turns traced to answers in session files.
   Seam-blind keep -> answer "I don't have it" (unused). rud1 keep (recall-pointer
   memory) -> answer numbers untraceable to the memory (unused). 2/2 keeps unused.
   Plus: keeps fire on empty prompts ("q" + trivia kept; 1,263 organic kept rows).
3. Base rate: dev pools constructed 22-26% relevant (44/170); heldout 5% (2/40).
   Keep precision 0.22 ~= pool prevalence -> at chance.
4. Threshold sweep (R146, 30 combos, $0 extra): keep precision never exceeds 0.23 at any
   cut -> the scorer carries no keep signal on this pool.

## Verdict (ranked)

1. Model + base rate (binding): scorer without keep signal on a low-prevalence pool;
   0.22 ~= chance, and no cut reaches 0.23.
2. Labels (not binding): kappa 0.41 caps cross-rater measurable precision ~0.4-0.6,
   well above observed 0.22 — noise cannot explain the gap.
3. Retry must change pool or decision structure (Choice top-k, graded rubric), not wording.

## Follow-up available (not run)

Full answer-join audit on 12 kept rows (`mem_use12.json` frozen): grep prompt substrings
in sessions, read next assistant turn, judge use. Method recorded; ~15 min keyless.
