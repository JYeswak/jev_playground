# PLAN REVIEW R2 — v4.1 @ `29038ab`

Target: `docs/PLAN-EVIDENCE-MATRIX.md` (399 lines). Round 2 of ≥4. Grok. No beads. No plan edit.

Round 1 landings that are real: vacuous dual named, wrong-event 0.381/0.605 retracted, `k` not bound as an outcome, `scope-disagreement` demoted, T6 split, case identity defined. Those were the right repairs. This round is whether the nine-edit pass introduced new lies. It did.

---

## (1) Re-derived §4.2 table — 0.20/0.30, Wilson z=1.96 two-sided

Formula: \(\hat p = k/n\), Wilson center \((\hat p + z^2/2n)/(1+z^2/n)\), half \(z\sqrt{(\hat p(1-\hat p)+z^2/4n)/n}/(1+z^2/n)\), \(z=1.96\).

FP legs (lower-better): point \(\hat p \le 0.20\), interval \(upper \le 0.30\).
Bind legs as the table's header at `:241-242` *also* claims, then contradicts: bind \(\hat p \ge 0.20\) and \(lower \ge 0.20\).

| row | k/n | p̂ | Wilson 95% | point≤0.20 | upper≤0.30 | table | match |
|---|---|---:|---|---|---|---|---|
| absence n=20 | 4/20 | 0.2000 | [0.0807, 0.4160] | **ok** (equal) | NO | ok / NO / REFUSE | yes, lo rounded 0.081 |
| absence n=77 | 21/77 | 0.2727 | [0.1858, 0.3812] | NO | NO | NO / NO / REFUSE | yes, 0.273 / [0.186, 0.381] |
| structural n=20 | 4/20 | 0.2000 | [0.0807, 0.4160] | **ok** | NO | ok / NO / REFUSE | yes |
| structural n=77 | 55/77 | 0.7143 | [0.6051, 0.8031] | NO | NO | NO / NO / REFUSE | yes |
| callsite n=20 | 6/20 | 0.3000 | [0.1455, 0.5190] | NO | NO | NO / NO / REFUSE | yes, [0.145, 0.519] |
| ft-rs 0/25 bind | 0/25 | 0.0000 | [0.0000, 0.1332] | bind: \(\hat p\ge0.20\) NO; \(lower\ge0.20\) NO | — | NO / NO / REFUSE | yes, 0.133 |
| ft-sh | **1/25** | 0.0400 | [0.0071, 0.1954] | bind both NO | — | 0.040 [0.007, 0.195] NO/NO | yes |

**Every numeric cell in the table is correct** under Wilson two-sided 95% and the 0.20/0.30 FP rule with `≤`. ft-sh is 1/25, not stated; the CI matches only that pair.

**The header of §4.2 is wrong.** `:241-242`:

> FP must satisfy `p̂ ≤ 0.30` **and** `upper ≤ 0.30`

That is the vacuous dual you just buried. The table is scored at 0.20/0.30. An implementer who reads the scoring rule, not the cells, rebuilds v2.

**§6 `:364-365` still says the validator *accepts* the 0/25 kills (CP upper 0.137 < 0.20).** The table *refuses* 0/25. Those are opposite inequalities:

- Kill-as-rarity (NEED #6, `NEEDS.md:35`): want \(upper < 0.20\) to show the class is small. 0/25 **passes** that test. Sound kill.
- Bind-as-precision (4.2): want \(\hat p \ge 0.20\) and \(lower \ge 0.20\) to *ship*. 0/25 **fails**. Don't ship.

Same operational outcome, different predicate, different `status`. `uncertified-pass` on a sound kill cannot be `passed`. T4 already wants kills/uncertified as `retired`. §6's "accepts" is leftover v2 prose. If you implement §6 literally, you mark ft-rs `passed` and the dual bar fights you.

Count: table has **7** rows. `:263` says **eight** rate-bearing decisions, five correct, three wrong. 3 ships + 2 kills + 2 relabel retires = 7. The eighth is invented.

---

## (2) `bar_point = 0.20` is reverse-engineered. Brutal, as asked.

The stated justification (`:203-207`): interval 0.30 is the old TTSR bar; point 0.20 is "two-thirds of it by the same reasoning he uses (0.80 is ~89% of 0.90)."

**0.80/0.90 = 0.889. 0.20/0.30 = 0.667.** Not the same reasoning. The parenthetical admits the ratios differ and proceeds anyway.

His two numbers mean different things: 0.90 is the *operating target* (precision we want), 0.80 is the *certification floor* (Wilson lower). Ours: 0.30 is a pre-existing FP cap. 0.20 is…

**0.20 = 4/20 = the ship-time \(\hat p\) of the two rules you need to look 'interval-only'.**

You wrote (`:255-260`) that the evidence the bars are real is that absence/structural at n=20 *clear the point bar and fail only the interval*. That sentence is the fitting criterion. Any `bar_point` in \((0.200, 0.273)\) makes n=20 point-ok and n=77 point-NO. You picked the left endpoint, **equal to the observed rate**, and used `≤` so 4/20 still "ok".

NEED #6, which you claim this plan encodes: **when \(\hat p\) lands on the bar, no n certifies.** You put the new point bar *on* \(\hat p\). The interval leg is the only thing refusing 4/20, which is where we were after round 1. The point leg's first "ok" is a sample sitting on its own bar.

Independent justifications that would have been honest:

- A loss: 1-in-5 fires wrong is wallpaper (R51's 55% was wallpaper; 20% is a different claim and needs an argument).
- Preregistered before seeing 4/20.

Neither exists. `0.20` was chosen so the table has a column of mixed ok/NO. That is the satisfying table. Do not freeze it in `authority.toml` until it has a reason that does not mention 4/20.

If you want both legs to bite *without* fitting: keep `bar_interval=0.30` (preregistered) and **drop `bar_point` until a target is justified**. A single interval bar is NEED #6. A second number that equals the data is a new vacuous trick.

---

## (3) `k-drift` + `label_rows_sha256` — closes transcription, not the labeller

Binding `k` in authority would let the reviewer set the result. Correct, do not do that.

Binding the **bytes** and recomputing `k` stops `k=0` with the same file. That was the hole I named. Transcription is closed.

**The hack moves one layer down, and it is R71.**

The party being measured authors `label_rows`. They label 77 TPs, 0 FPs. Validator recomputes `k=0`. `k-drift` agrees. `p̂=0`, Wilson upper ≈ 0.047, both 0.20/0.30 legs pass. `unpersisted-rate` only checks `len(keys) ≥ n` (`:155`), not that gold is honest. Hash changes, so they edit `label_rows_sha256` in `authority.toml`. Second key is still Joshua (`:138-140`). If he reviews a hash and not 77 rows, rubber stamp. T4's *first* freeze is the scoring party writing the hash (`T4 Depends: T2`, not T5 — `:312-314`).

sha256 is tamper-evidence *after* a trusted labelling. It is not a labelling oracle. R70/R71 were "ships had no rows" and "two samples cannot be the same population." Checksums do not pick the correct population.

Also: the schema example hash `e3b0c442…` (`:113`) is SHA-256 of the **empty string**. Do not teach that.

What would actually close it:

- Freeze **bars, n, method, sampling frame** before any labels exist (timestamp, not hash of outcomes).
- `k` = count of a **named gold field**, schema-checked (`gold ∈ {FP,TP}`), mutation-twinned.
- Same-commit ban: `authority.toml` hash and `label_rows` cannot land together.
- Steward ≠ scorer on the authority row.
- `unpersisted-rate` checks gold histogram, not key count.

Until then: k-drift is necessary and not sufficient. Say that in §3 instead of "why that is not a hole."

---

## (4) Reward hacks against v4.1

Closed: transcribe `k` downward on frozen rows.

Still open:

1. Relabel gold (above).
2. `status` never `passed`; ship `.omp/rules/*.md` anyway. Still no rule-file walk. F6 lives.
3. Omit `rate` entirely — no dual bar, no k-drift.
4. `non_claims` substring. Schema example (`:115-117`) is still the exploit. v4.1 did not take the typed-field fix.
5. Method identifier contains `independent` while rows are overlapping session fires.
6. `loss_evidence` file authored by the same pane, control loses by construction. `control-not-beaten` has no loss grammar. `:224-225` still says FP 0.714 fails always_quiet "without any labelling at all" — still false.
7. `scope-unverified`: commit on a machine without omp. `:176-178` skip-with-named-reason. If `gates.sh` exits 0, that is skip-as-pass with a sticker. Distinct state is necessary, not sufficient — `passed` + `scope-unverified` must be illegal.
8. `title` still bound (`:124`). Noise burns the second key.
9. T6b `Depends: T4` while acceptance is a temp fixture (`:341-346`). Agent following Depends waits; agent following Acceptance doesn't. Pick one.
10. Implement §4.2 header (`p̂ ≤ 0.30`) not §4.1 (`0.20/0.30`). Green table, vacuous code.

---

## (5) What round-1 fixes broke

1. **§4.2 scoring rule vs §4.1 bars.** Header restored the vacuous dual in the one place an implementer copies.
2. **§6 vs §4.2 on 0/25.** Accept vs refuse. Kind-direction never written into the schema. FP uses upper; bind uses lower; kill-as-rarity uses upper. Three predicates, one word REFUSE.
3. **Point bar sits on 4/20.** NEED #6 applied to the new leg.
4. **T6b still depends on T4** after you "split per my objection." The temp-fixture acceptance is the actual fix; the Depends line undoes it.
5. **T2 lists eight codes; §6 still wants nine planted violations.** `no-mutation-twin` is in the table (`:162`) and not in T2's eight (`:299-302`). Fresh agent guesses again.
6. **§8 still says Axis B is in flight** (`:394`). Header says all four axes committed (`:3`).
7. **Joshua still holds the second key** after you accepted that this is theatre. The hash is the interesting key; the sentence at `:138` contradicts §3's own k paragraph.
8. **always_quiet / non_claims** unchanged after an accepted refusal.

T6a `--list-cases` is a real improvement. T8 is still ceremony.

---

## (6) Seventh question, answered against v4.1

Round 1 did answer it (artifact §7 table). You are right that the vacuous dual proves the risk, so here it is again, scored on *this* text, not on goodwill.

Rule 12: adopt the mechanism that fits F1–F6. Refuse slogans. Vacuous 0.30/0.30 was adopting a *shape*. 0.20/0.30 is adopting a *ratio you invented from our 4/20*. That is not better.

| 4.1 item | Evidence it fits *our* failures | v4.1 |
|---|---|---|
| Distinct dual thresholds | Interval bar 0.30: yes, NEED #6, preregistered. Point bar 0.20: **no** independent evidence; equals ship-time \(\hat p\); 2/3 ≠ 8/9. | **Interval: keep. Point: do not freeze.** |
| Method name carries iid | Our defect is overlapping fires treated as iid. His string is one-primary-case-per-family. Copying the string is a false assumption. | **Adopt `iid_claimed: bool`. Refuse his identifier.** |
| ≥3 non-claims as phrases | Does not catch F1 or F3. Schema example is the bypass. His phrases describe a synthetic fixture; our rows are live rules. | **Still refuse.** Typed `labeller_count`, `iid_claimed`. |
| always_quiet must lose | No 0/1/2 table. "Without labelling" is false. | **Still refuse** until loss exists. |
| Mutation twins | Dead RED arms, UBS empty-scan-set. Measured here. | **Still adopt.** |
| `label_rows_sha256` + recompute k | F1/R70 tamper-evidence. Does not fix F2/R71 labeller. | **Adopt as checksum. Do not call it the hole closed.** |
| Joshua as second key | F3 was same party. He is that party. | **Refuse.** Time-freeze bars; hash labels; steward ≠ scorer. |

The proof you asked for that wholesale-adopt is real: you took "two different numbers" from a precision metric, inverted the direction for FP, set the new number equal to the sample, and wrote that the mixed ok/NO column *is the evidence the bars are real*. That is authority (his dual-bar *exists*) over evidence (what 0.20 means for an FP rate in this fleet).

---

## Diffs for v4.2 (minimal)

```diff
-Every rate-bearing decision … FP must satisfy `p̂ ≤ 0.30` **and** `upper ≤ 0.30`
+FP (`rate.kind=fp`): `p̂ ≤ bar_point` and `upper ≤ bar_interval`, bars from authority.
+Bind-to-ship (`kind=bind`): `p̂ ≥ bar_point` and `lower ≥ bar_interval`.
+Kill-as-rarity is the FP direction. Do not mark it `passed`.

-accepts the 0/25 kills (CI upper 0.137 < 0.20 bar)
+refuses `status=passed` on 0/25 under bind-to-ship; records `retired` (sound kill).
+Do not cite CP 0.137 here unless `rate.method` is CP.

-bar_point = 0.20 is set at two-thirds of it by the same reasoning he uses (0.80 is ~89% of 0.90)
+bar_point is NOT JUSTIFIED. Do not put 0.20 in authority.toml. Interval 0.30 stays.
+If a point bar is required, preregister it without reference to 4/20.

-Why k is not in that list, and why that is not a hole.
+k-drift closes transcription. Labeller-authored rows remain F2. Hash is checksum, not oracle.

-Who holds the second key. Joshua.
+Bars frozen before labels. Hash frozen after labels, different commit. Scorer ≠ authority author.

-non_claims = ["not a live measurement", "single labeller", "rows not independent…"]
+labeller_count = 1
+iid_claimed = false

-T6b *Depends:* T6a, T4
+T6b *Depends:* T6a only. Acceptance already uses mktemp.

-nine planted violations
+planted count = T2's eight + T3's remainder, listed once.

-Axis B … is **in flight**
+Axis B landed; this sentence is stale.
```

Plus: `passed` ∧ `scope-unverified` is a hard fail. Example hash must not be the empty digest. Drop T8 or say it is optional.

---

## Boundary

- Wilson z=1.96 two-sided, stdlib, this session. CP 0.137 for 0/25 taken from `NEEDS.md:35`, not recomputed with scipy.
- ft-sh k=1 n=25 inferred from the published CI; the plan does not state k.
- Did not edit the plan. Did not run a validator that does not exist yet.
