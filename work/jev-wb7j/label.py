#!/usr/bin/env python3
"""jev-wb7j: blind human labels (WildCarp, 2026-10-01).

Rule (from BAR.md): RELEVANT if a competent engineer would use that
memory to answer or act on that prompt; borderline -> RELEVANT.
Written BEFORE any live Jev call (blind).
"""

LABELS = {
    # P0: adversarial full review of 0927 plan + 18 beads (read-only)
    "S000": "RELEVANT",  # live gate-shadow hook fix bears on P5 gate-shadow review
    "S001": "IRRELEVANT",  # generic retain-tool guidance
    "S011": "IRRELEVANT",  # content-free fragment
    "S014": "RELEVANT",  # eval disclosure practice bears on evidence standards
    "S020": "IRRELEVANT",  # pane coordination, not review-usable
    "S022": "IRRELEVANT",  # pane coordination
    "S026": "IRRELEVANT",  # fragment
    "S030": "RELEVANT",  # pinned model id fact bears on plan consistency
    "S035": "IRRELEVANT",  # fragment
    "S039": "IRRELEVANT",  # fragment
    "S046": "IRRELEVANT",  # renderer test status, task says no tests
    "S050": "IRRELEVANT",  # opaque commit pointer
    "S058": "IRRELEVANT",  # generic memory-system description
    "S063": "IRRELEVANT",  # ops status
    "S069": "RELEVANT",  # receipt-generation practice bears on evidence review
    "S072": "IRRELEVANT",  # opaque
    "S073": "IRRELEVANT",  # pane coordination
    "S076": "IRRELEVANT",  # labeling progress
    "S080": "IRRELEVANT",  # progress fragment
    "S099": "IRRELEVANT",  # progress fragment
    # P1: second-reader review of committed objects
    "S002": "IRRELEVANT",
    "S012": "IRRELEVANT",
    "S013": "IRRELEVANT",
    "S059": "IRRELEVANT",
    "S068": "RELEVANT",  # live web-rerank receipt bears on activation checks
    "S077": "IRRELEVANT",
    "S092": "IRRELEVANT",  # generic recall guidance
    "S096": "IRRELEVANT",  # opaque session id
    # P2: W5 snapshot review
    "S003": "IRRELEVANT",
    "S015": "IRRELEVANT",  # generic conflict-precedence guidance
    "S016": "IRRELEVANT",
    "S021": "IRRELEVANT",
    "S043": "IRRELEVANT",  # opaque hash
    "S047": "IRRELEVANT",
    "S049": "IRRELEVANT",
    "S054": "IRRELEVANT",
    "S085": "IRRELEVANT",
    "S093": "IRRELEVANT",
    "S095": "IRRELEVANT",
    "S098": "RELEVANT",  # live gate-scored receipt bears on P2/P8 gate language
    # P3: W6 snapshot review
    "S004": "IRRELEVANT",
    "S006": "IRRELEVANT",
    "S008": "IRRELEVANT",
    "S031": "IRRELEVANT",
    "S034": "IRRELEVANT",
    "S044": "IRRELEVANT",
    "S051": "IRRELEVANT",
    "S056": "IRRELEVANT",  # README verbs evidence, outside review criteria
    "S084": "RELEVANT",  # pinned model id fact
    "S088": "IRRELEVANT",
    "S091": "IRRELEVANT",
    # P4: source-reality audit P8/P13/P14
    "S005": "RELEVANT",
    "S007": "IRRELEVANT",
    "S009": "IRRELEVANT",
    "S010": "RELEVANT",  # receipt-generation practice bears on source tracing
    "S024": "RELEVANT",  # gate-scored receipt, hook evidence in slice
    "S025": "RELEVANT",  # gate-shadow hook live, observe-only-hook question
    "S040": "IRRELEVANT",
    "S045": "IRRELEVANT",
    "S048": "IRRELEVANT",
    "S055": "RELEVANT",  # sample-rate caveat bears on scoring methodology
    "S062": "IRRELEVANT",
    "S065": "IRRELEVANT",
    "S067": "IRRELEVANT",
    "S070": "IRRELEVANT",
    "S079": "IRRELEVANT",  # kit coordination, outside slice
    "S090": "IRRELEVANT",
    # P5: source-reality audit P2-P7/U04/U06/U07, gate evidence
    "S017": "RELEVANT",  # web-rerank receipt, gate evidence in slice
    "S019": "RELEVANT",  # gate-scored receipt, directly in slice
    "S023": "IRRELEVANT",
    "S027": "IRRELEVANT",
    "S037": "IRRELEVANT",
    "S041": "IRRELEVANT",
    "S042": "IRRELEVANT",
    "S053": "IRRELEVANT",
    "S064": "RELEVANT",  # sample-rate caveat, scoring methodology
    "S094": "IRRELEVANT",
    # P6: full review #2 committed objects
    "S018": "IRRELEVANT",
    "S028": "RELEVANT",  # planted README drift RED bears on integrity checks
    "S029": "IRRELEVANT",
    "S032": "IRRELEVANT",
    "S038": "IRRELEVANT",
    "S057": "RELEVANT",
    "S060": "IRRELEVANT",
    "S066": "IRRELEVANT",
    "S075": "IRRELEVANT",
    "S078": "IRRELEVANT",
    "S089": "IRRELEVANT",
    # P7: docs correction task
    "S033": "IRRELEVANT",  # grep-proof practice not usable for README/EVAL edit
    "S074": "RELEVANT",  # committed-blob hashing guidance usable for EVAL entry
    # P8: source-reality audit P1/P9/P11/P12, HealthVer/kit/SDK
    "S036": "IRRELEVANT",
    "S052": "IRRELEVANT",
    "S061": "IRRELEVANT",
    "S071": "IRRELEVANT",
    "S082": "IRRELEVANT",
    "S083": "IRRELEVANT",
    "S086": "IRRELEVANT",  # hook evidence, hooks outside this slice
    "S087": "RELEVANT",  # README drift RED bears on README-receipt slice
    # P9: verify jev-4nyy receipt (counts in session files)
    "S081": "RELEVANT",  # grep-proof practice directly usable for verification
    "S097": "RELEVANT",  # no-stash rule usable on shared tree
}

if __name__ == "__main__":
    import json

    assert len(LABELS) == 100, len(LABELS)
    with open("work/jev-wb7j/sample.jsonl") as fh:
        rows = [json.loads(l) for l in fh]
    ids = {r["id"] for r in rows}
    assert set(LABELS) == ids, "id mismatch"
    with open("work/jev-wb7j/labels.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps({"id": r["id"], "label": LABELS[r["id"]]}) + "\n")
    from collections import Counter

    print(Counter(LABELS.values()))
