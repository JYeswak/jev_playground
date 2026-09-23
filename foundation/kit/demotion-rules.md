# Demotion rules (installed copy)

Ported 2026-09-23 from `/tmp/jev-rc-p1/fa48/starter-kit/templates/demotion-rules.md`
(v8 assessment pack, byte-identical to v7). This is the working copy the kit
executes; the template is the reference. Which rules this repo can execute
today is stated at the bottom — a rule nothing reads is not an application.

Demotion is the machinery that moves claims *down* when evidence weakens.
Promotion needs a gate; demotion needs only counter-evidence. Adapted from
frankenfs's multi-layer pattern — the most developed in the suite
(docs/planning/MODULARITY_RUNBOOK.md, docs/runbooks/readiness-action-autopilot.md,
docs/LEDGER_RESURRECTION.md). Each rule is marked [MECHANICAL] (enforced by a
script) or [PROCEDURAL] (enforced by convention and review). This starter set
is deliberately procedural-first: only 5 of 44 suite projects achieved
mechanical auto-demotion, so the kit does not pretend it is day-one cheap.

## D1 — Claim-effect lattice [PROCEDURAL]

- **Trigger:** advisory (weak) evidence arrives about a claim.
- **Action:** advisory inputs may only `no_change`, `block_upgrade`, or `downgrade_required`. The `upgrade_eligible` effect is reserved for authoritative proof.
- **Override:** none — an upgrade on advisory evidence is a gate violation, not a judgment call.
- **Origin:** frankenfs docs/runbooks/readiness-action-autopilot.md §4.

## D2 — Open P0 blocks release claims [PROCEDURAL → MECHANICAL at maturity]

- **Trigger:** a priority-0 issue is open.
- **Action:** no release-readiness claim may be made until the P0 is closed or reprioritized with recorded evidence.
- **Override:** reprioritization requires the evidence for the new priority, written down.
- **Mechanical form (maturity):** a test asserting release-readiness is blocked by an open P0 (frankenfs: `release_readiness_blocked_by_open_p0`).
- **Origin:** frankenfs docs/tracker-hygiene.md.

## D3 — Gate-change rule [PROCEDURAL]

- **Trigger:** someone proposes changing a gate's thresholds, counters, or exception semantics to land a change.
- **Action:** the change requires evidence in both directions: cases newly admitted as valid AND cases that remain rejected. A gate may never be weakened to land a change.
- **Override:** none.
- **Origin:** frankenfs docs/planning/MODULARITY_RUNBOOK.md ("Changing thresholds, counters, or exception semantics is a gate change"); frankenredis docs/GATE_VALIDITY.md.

## D4 — Demotions are always allowed [PROCEDURAL]

- **Trigger:** counter-evidence against any claim, from any agent.
- **Action:** any agent may demote the claim immediately, no permission needed. Record the demotion and the evidence in the negative-evidence ledger.
- **Override:** n/a — this rule exists to make demotion cheaper than silence.
- **Origin:** frankensim docs/MATURITY_LEVELS.md ("Demotions are always allowed and are never blocked").

## D5 — Tombstoning [PROCEDURAL]

- **Trigger:** a claim is retired.
- **Action:** the claim id stays in `registries/claims.tsv` marked `retired` in notes; it is never reused and never deleted. Future agents must be able to see what was claimed and why it died.
- **Override:** none.
- **Origin:** frankensympy registries/claims.toml ("retired claim IDs must remain").

## D6 — Proof expiry [PROCEDURAL → MECHANICAL at maturity]

- **Trigger:** a claim's proof is older than 90 days and was attested manually (not by a machine-checkable artifact).
- **Action:** the claim demotes to `implemented_uncertified` until re-verified.
- **Override:** re-verification resets the clock.
- **Mechanical form (maturity):** the claim registry carries proof dates; the claim-discipline check fails expired manual proofs.
- **Origin:** frankentui docs/claims-ledger.md ("manual: proofs expire after 90 days").

## D7 — SHA-mismatch auto-demotion [MECHANICAL at maturity]

- **Trigger:** an artifact's hash does not match the registry.
- **Action:** automatic demotion — not reviewer-overridable, not waivable.
- **Override:** none. Fix the artifact or fix the registry; do not patch around the mismatch.
- **Origin:** frankengit registries/claims.tsv + docs/VERIFY_SPEC.md.

## Executed in this repo today

One mechanical tooth, landed with this file: `foundation/kit/check-demotion.sh`,
wired as gate stage `foundation/gates.d/17-kit-demotion.sh`. Every `enforce=yes`
row in `foundation/kit/claims.tsv` must resolve to an existing non-empty proof
file; a missing proof demotes the claim (exit 1, `DEMOTE` line naming the row).
That is the proof-exists slice of D7, applied to enforced rows only.

The rest stays procedural, with the consumer named where one exists:

- D1 lattice: procedural. `claims.tsv` tags no evidence as advisory vs
  authoritative, so no script can enforce the effect split.
- D2 open P0: procedural. No P0 tracker is wired to the claim registry.
- D3 gate-change: procedural. Enforced by review; the `check-demotion.sh`
  selftest convention (plant a RED arm, require the trip) is the local form.
- D4 always allowed: procedural. The ledger is `NEGATIVE_EVIDENCE.md` at the
  repo root; any agent demotes by writing there with a retry condition.
- D5 tombstoning: procedural. `claims.tsv` currently holds one row and no
  retired ids; the first retirement tests this rule.
- D6 expiry: procedural. `claims.tsv` carries no proof dates, so nothing can
  compute expiry. The maturity form is stated in the rule for whoever adds the
  column.
- D7 hash match: procedural beyond exists-and-nonempty. No sha256 manifest
  covers the proof artifacts yet.
