# Source-linked conversion exemplar

## What the Franken projects actually do

| Evidence | Mechanism | Adopt / limit |
|---|---|---|
| `franken_node/.beads/bulk_import.md:1-19` | An intermediate bead manifest groups epics with type, priority, labels and full descriptive bodies. | Adopt reviewed issue-shaped contracts before issuing `br` writes. It is a manifest, not a proved automatic plan parser. |
| `frankensqlite/docs/planning/PROPOSED_BEADS_2026-05-19.import.sh:1-76` | Two passes: `new` executes `br create --json`, stores `logical_name → returned_id`, then `dep` executes `br dep add`. `set -euo pipefail` and `br doctor --quick --json` preflight. | Adopt returned-ID map and CLI-only writes. **Do not copy** title-only skip (wrong scope can reuse a title), `dep` returning success for a missing endpoint, or swallowing `br dep add` errors at lines 75–83. Pass `--actor` on writes. |
| `franken_ocr/docs/PROPOSED_ARCHITECTURE.md:920-930` | A plan section maps to testable issues: a kernel becomes implementation + parity + benchmark obligations; open questions become spikes. | Plan IDs map to **contracts**, not always literal heading/issue 1:1. Preserve real proof prerequisites. |
| `frankensympy/tools/validate_planning.py:1-95` | Validates a proposal artifact before downstream use. | A parse/shape check cannot decide whether an operator exists or the execution DAG implements the product. |

These are distinct cases, not evidence that every Franken repository uses one converter. The shared repeatable part is an explicit source→issue map, two-phase CLI creation, and graph/consumer verification.

## Tiny explicit mapping (illustrative; do not execute blindly)

Input from a reviewed plan, not inferred by regex:

| Plan contract | Activation | Required predecessor | Bead result in Jev on 2026-09-28 |
|---|---|---|---|
| P15 contain automatic egress | Execution root | none | `jev-p15-contain-automatic-egress-810p` |
| P0 identify real consumer | Execution root | none | `jev-p0-identify-consumer-e8uf` |
| P1 stranger baseline | Execution | P0, even when P0 concludes NO_CONSUMER | `jev-p1-stranger-baseline-przc` |
| P9 public quickstart | Execution | P1 | `jev-p9-stranger-quickstart-2srw` |
| P2–P8, P11–P14 | Conditional | named demand/safety/independent evidence; not mechanically P0 | `NOT_ACTIVATED`, no speculative beads |
| P10 | Conversion operation | user approval | no self-justifying conversion bead |

P15 and P0 run independently when execution is released. P9 does not require P15 unless the actual quickstart sends automatic Jev traffic; a documentation path is not an automatic hook. This mapping is tied to the reviewed `docs/0927_reality_plan.md` and its user halt; on a different plan derive a new map from its consumer/action contracts.

Controller shape (invoke `br` as an external process, do not modify `.beads/issues.jsonl` directly):

```python
# Pseudocode, deliberately not a generic plan parser.
entries = [
    {"plan_id": "A", "slug": "a", "body": "WHAT/WHY/ACCEPTANCE...", "deps": []},
    {"plan_id": "B", "slug": "b", "body": "...", "deps": ["A"]},
]
assert len({e["plan_id"] for e in entries}) == len(entries)
id_by_plan_id = {}
for entry in entries:
    # Inspect existing issues for semantic owner first; reusing a title is insufficient.
    issue = checked_br_create_json(entry["slug"], entry["body"], actor=agent)
    id_by_plan_id[entry["plan_id"]] = issue["id"]
for entry in entries:
    for predecessor in entry["deps"]:
        assert predecessor in id_by_plan_id  # or explicitly verified external ID
        checked_br_dep_add(id_by_plan_id[entry["plan_id"]], id_by_plan_id[predecessor], actor=agent)
# Read back each issue/dependency; check cycles, ready-state and source coverage.
```

The pseudocode is intentionally **not executable**: converting prose directly into runnable work is a human/agent judgment, and every repo has its own halt, existing ownership and dependency semantics. Use `br create --description-file - --json` to avoid shell quoting in real commands. Error from a write means stop, inspect actual store state, then resume from returned/read-back IDs; never rerun the whole importer on a title match.

## Negative controls for a conversion audit

- Rename an existing issue but retain its plan ID: source-ID mapping should still find it. Reuse its title for a different scope: refuse duplication/reuse until semantics are checked.
- Remove a direct predecessor: dependency audit should fail even if `br dep cycles` remains empty.
- Give a conditional alternative the predecessor of a closed branch: refuse to infer it is ready without its own wake trigger.
- Halt implementation after conversion: `br ready --json` should show no **new** converted issue; pre-existing assignments remain untouched.
- Hand only the most obscure bead body to a stranger: if it needs the plan to identify its positive, refusal, owner or non-claims, edit the bead before calling conversion done.
