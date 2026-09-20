import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { baseline, shipPredicate, confusion, toState, hybridVerdict } from "./baseline.mjs";

const root = dirname(fileURLToPath(import.meta.url));
const { cases } = JSON.parse(readFileSync(join(root, "cases.json"), "utf8"));

test("SHIP: hits, rate, unlabelled, no concentration", () => {
  assert.equal(
    baseline({ hits: 820, rate: 1.05, FP: null, concentration_top_session_share: null }),
    "SHIP",
  );
  assert.equal(shipPredicate({ hits: 820, rate: 1.05, FP: null, concentration_top_session_share: null }), true);
});

test("FP exactly 0.30 still ships (inclusive bar)", () => {
  assert.equal(
    baseline({ hits: 64, rate: 0.08, FP: 0.3, concentration_top_session_share: null }),
    "SHIP",
  );
});

test("hits 14 is TOO_RARE even with a passing rate", () => {
  assert.equal(
    baseline({ hits: 14, rate: 0.02, FP: null, concentration_top_session_share: null }),
    "REFUSE_TOO_RARE",
  );
  assert.equal(shipPredicate({ hits: 14, rate: 0.02, FP: null, concentration_top_session_share: null }), false);
});

test("rate above 5 is NUISANCE, not TOO_RARE", () => {
  assert.equal(
    baseline({ hits: 4000, rate: 6.1, FP: null, concentration_top_session_share: null }),
    "REFUSE_NUISANCE",
  );
});

test("labelled FP 0.67 is LOW_PRECISION even inside the rate bar", () => {
  assert.equal(
    baseline({ hits: 965, rate: 1.23, FP: 0.67, concentration_top_session_share: null }),
    "REFUSE_LOW_PRECISION",
  );
});

test("concentration 0.73 is UNDERPOWERED only after numeric bars pass", () => {
  assert.equal(
    baseline({ hits: 329, rate: 0.73, FP: null, concentration_top_session_share: 0.73 }),
    "UNDERPOWERED",
  );
});

test("FP is checked before concentration: claim-verb-shaped row is LOW_PRECISION", () => {
  assert.equal(
    baseline({ hits: 329, rate: 0.729, FP: 0.9167, concentration_top_session_share: 0.73 }),
    "REFUSE_LOW_PRECISION",
  );
});

test("v2-files (hits=10) is TOO_RARE on the cascade, not UNDERPOWERED", () => {
  assert.equal(
    baseline({ hits: 10, rate: 0.0128, FP: null, labelled_n: 10, concentration_top_session_share: null }),
    "REFUSE_TOO_RARE",
  );
});

test("toState strips id and gold so the model cannot read the label", () => {
  const state = toState(cases[0]);
  assert.equal("id" in state, false);
  assert.equal("gold" in state, false);
  assert.deepEqual(
    Object.keys(state).sort(),
    [
      "FP",
      "N",
      "concentration_top_session_share",
      "corpus_is_authored_by_us",
      "description",
      "examples",
      "hits",
      "is_defect_or_routing",
      "labelled_n",
      "name",
      "predicate",
      "rate",
      "seed",
    ].sort(),
  );
});

test("19 gold cases: baseline SHIPS the three semantic rows (the known miss)", () => {
  assert.equal(cases.length, 19);
  const rows = cases.map((c) => ({ gold: c.gold, pred: baseline(c) }));
  for (const row of rows) assert.equal(typeof row.pred, "string");
  for (const id of ["digest-truncation", "path-nonexistence", "pipefail-masked"]) {
    const row = cases.find((c) => c.id === id);
    assert.equal(row.row_kind, "semantic");
    assert.equal(row.gold_noul, false);
    assert.equal(baseline(row), "SHIP");
  }
  const { correct } = confusion(rows, "pred");
  assert.equal(correct, 14);
});

test("hybrid does not call Jev when numbers already refuse", () => {
  const h = hybridVerdict({ hits: 14, rate: 0.02, FP: null, concentration_top_session_share: null }, 0.99, 0.5);
  assert.equal(h.called, false);
  assert.equal(h.verdict, "REFUSE_TOO_RARE");
});

test("hybrid vetoes a numeric SHIP when noul is below threshold", () => {
  const c = { hits: 827, rate: 1.06, FP: null, concentration_top_session_share: null };
  assert.equal(shipPredicate(c), true);
  const h = hybridVerdict(c, 0.09, 0.5);
  assert.equal(h.called, true);
  assert.equal(h.veto, true);
  assert.equal(h.verdict, "REFUSE_NUISANCE");
});

test("hybrid keeps a numeric SHIP when noul is at threshold", () => {
  const h = hybridVerdict({ hits: 64, rate: 0.08, FP: 0.3, concentration_top_session_share: null }, 0.5, 0.5);
  assert.equal(h.veto, false);
  assert.equal(h.verdict, "SHIP");
});

test("hybrid does not silently ship a survivor with missing noul", () => {
  const h = hybridVerdict({ hits: 820, rate: 1.05, FP: null, concentration_top_session_share: null }, null, 0.5);
  assert.equal(h.missing, true);
  assert.equal(h.verdict, null);
});
