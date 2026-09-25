# PokéJev component held-out result

**Lane:** offline; existing Jev answers only; zero live requests and zero battle runs.
**Model recorded in the source rows:** `jev-1.13.0`. **Split:**
`decision-split-v1.json` (`d10605fa534597820d159c60a723344561a40bf60ed77ff00dedaba4e05d340d`).
**Frozen alphas:** player `0.40`, opponent `0.25`, fit on the 1,000-row dev side only.

Each row is paired with the deterministic usage floor. Bootstrap uses 5,000 resamples;
95% intervals are deterministic (player seed `20260925`, opponent seed `20260926`).
Log-loss uses all 1,000 rows; labels outside candidate support receive probability `1e-6`.
`coverage` is reported separately.

| Component | N | Floor top-1 | Mixture top-1 (95% CI) | Paired Δ top-1 (95% CI) | Floor log-loss | Mixture log-loss (95% CI) | Paired Δ log-loss (95% CI) |
|---|---:|---:|---:|---:|---:|---:|---:|
| player (`alpha=0.40`) | 1000 | 0.3450 | 0.4150 [0.3850, 0.4470] | +0.0700 [+0.0430, +0.0970] | 1.7455 | 1.6061 [1.5512, 1.6641] | -0.1395 [-0.1781, -0.1015] |
| opponent (`alpha=0.25`) | 1000 | 0.1770 | 0.2460 [0.2190, 0.2730] | +0.0690 [+0.0410, +0.0960] | 2.8478 | 2.7385 [2.6192, 2.8643] | -0.1092 [-0.1447, -0.0782] |

Opponent candidate-support coverage is `0.975`; player coverage is `1.000`. The paired
mixture improves both top-1 and all-row log-loss on this held-out split. This is a component
signal only; it is not a battle-level result and does not authorize a battle run by itself.

Machine-readable receipt: `heldout-v1.json`.
