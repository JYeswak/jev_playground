# Live smokes — index

One row per `demos/*/live-receipt.json`. Each receipt is a single `--live` run through `askJevBundle`, model `jev-1.13.0`, recorded with its actions, model, and call count. Read the linked receipt for the numbers; this file runs nothing.

| demo | command | calls | model | note |
|---|---|---|---|---|
| autoformat | `node demos/autoformat/demo.mjs --live` | 2 | jev-1.13.0 | All six markers render in both lanes. Two items differ: live did not join the wrapped "shadow / mode" line (fixture joins 2, live 1) and typed the closing sentence as a list item. Re-recorded 2026-09-24; the 2026-09-22 receipt recorded a demo bug, one unnamed question for every block. ([receipt](autoformat/live-receipt.json)) |
| cascade | `node demos/cascade/demo.mjs --live` | 1 | jev-1.13.0 | Fixture escalates location (0.71); live escalates registration_open_date (0.76) and passes location (0.18). ([receipt](cascade/live-receipt.json)) |
| chief | `node demos/chief/demo.mjs --live` | 4 | jev-1.13.0 | Agrees on 3 of 4 jobs; vague-ask routes research live vs review fixture. ([receipt](chief/live-receipt.json)) |
| citation | `node demos/citation/demo.mjs --live` | 4 | jev-1.13.0 | Two verified, two contradicted and sent to review; power_ten never reached the model (missing from source). Differs from the fixture on one claim: shipping_free was says_nothing / unsupported there and contradicts / contradicted live; it goes to review in both lanes. ([receipt](citation/live-receipt.json)) |
| compact | `node demos/compact/demo.mjs --live` | 1 | jev-1.13.0 | Fixture kept t3 call and dropped its tail; live dropped all three calls. ([receipt](compact/live-receipt.json)) |
| consistency | `node demos/consistency/demo.mjs --live` | 3 | jev-1.13.0 | 6 of 8 questions hold a gated plurality at gate 0.60; primary_risk and link_handling go to review. Differs from the fixture on 6 of 8: given the post, Jev reads the threat as violence (Violence, Strike, Threat, High) where the fixture had harassment (Harass, Remove, General, Medium). Re-recorded 2026-09-24 with the cookbook post and questions; the 2026-09-22 run sent only the post id (jev-fbhe). ([receipt](consistency/live-receipt.json)) |
| consistency-noul | `node demos/consistency-noul/demo.mjs --live` | 3 | jev-1.13.0 | 10 of 14 questions hold a non-uncertain plurality; band 0.30-0.70. Differs from the fixture on 1 of 14: docs_sufficient is uncertain live (0.32, 0.29, 0.30) where the fixture said no. Re-recorded 2026-09-24 with the cookbook claim and questions; the 2026-09-22 run sent only the claim id (jev-fbhe). ([receipt](consistency-noul/live-receipt.json)) |
| date | `node demos/date/demo.mjs --live` | 6 | jev-1.13.0 | Fixture leaves kickoff unassembled (none); live assembled 2026-08-14 at 0.33 under review. ([receipt](date/live-receipt.json)) |
| entity | `node demos/entity/demo.mjs --live` | 4 | jev-1.13.0 | Same-pair asserted sameAs, diff-pair left unlinked, fruit-variant and style-words to the curator queue: all four outcomes match the fixture. ([receipt](entity/live-receipt.json)) |
| guard | not recorded | 4 | jev-1.13.0 | Dosage blocked live (severity 2.1 over block 2); fixture had it under review. ([receipt](guard/live-receipt.json)) |
| hierarchy | `node demos/hierarchy/demo.mjs --live` | 10 | jev-1.13.0 | Beam agrees on both docs. Greedy differs on pie-recipe: the fixture root split tech-first, the live root food-first, so live greedy never made the mistake beam exists to repair. Re-recorded 2026-09-24; the 2026-09-22 receipt recorded a demo bug, routing on an unresolved Promise. ([receipt](hierarchy/live-receipt.json)) |
| parallel | `node demos/parallel/demo.mjs --live` | 1 | jev-1.13.0 | Same answers live as fixture within noise. ([receipt](parallel/live-receipt.json)) |
| preparsed | `node demos/preparsed/demo.mjs --live` | 4 | jev-1.13.0 | Same extractions live as fixture; all verbatim and normalization checks held. ([receipt](preparsed/live-receipt.json)) |
| rag | `node demos/rag/demo.mjs --live` | 5 | jev-1.13.0 | Fixture kept sessions-01 as conflicting_evidence; live drops all five. ([receipt](rag/live-receipt.json)) |
| rerank | `node demos/rerank/demo.mjs --live` | 10 | jev-1.13.0 | Both queries ranked the wanted document first. ([receipt](rerank/live-receipt.json)) |
| semantic-find | `node demos/semantic-find/demo.mjs --live` | 2 | jev-1.13.0 | Both checks held live. ([receipt](semantic-find/live-receipt.json)) |
| skill-suggest | `node demos/skill-suggest/demo.mjs --live` | 6 | jev-1.13.0 | Same three outcomes live as fixture. ([receipt](skill-suggest/live-receipt.json)) |

NO-CLAIM: an index is not a new measurement.
