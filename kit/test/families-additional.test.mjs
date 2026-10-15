// Cohort-B adapter invariants, source-description scope only (jev-b35c.17.2).
//
// Covers what exists in-tree: the seven source verbs are exposed in the
// family-verb record (a missing verb fails), and the committed-evidence path
// (registry capabilities/schema/validation, decision contracts) stays green.
// Memory-enforcement live switch and effort shadow-only have NO executable
// subject in-tree (no adapter implementation, no effort routing code found by
// search 2026-10-15) and are explicitly NOT covered here; they belong to
// jev-b35c.17.1 (open) or director routing. No model calls, no network.
// NO-CLAIM: this pins source-description invariants, not adapter behavior.

import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  createFamilyRegistry,
  validateFamilyNames,
} from "../src/families/registry.ts";
import { validateContract } from "../src/contracts.ts";

const SOURCE_VERBS = [
  "run",
  "batch",
  "explain",
  "cases",
  "eval",
  "calibrate",
  "watch",
];

const familyNamed = (name) => [{ name, usage: "x", description: "x" }];

for (const verb of SOURCE_VERBS) {
  test(`source verb '${verb}' is exposed (reserved as a family name)`, () => {
    const errors = validateFamilyNames(familyNamed(verb));
    assert.ok(
      errors.some((message) => message.includes("reserved family name")),
      `verb '${verb}' must be reserved; got: ${JSON.stringify(errors)}`,
    );
  });
}

test("committed registry generates capabilities, docs and schema", () => {
  const registry = createFamilyRegistry();
  assert.deepEqual(registry.validateFamilyNames(), []);
  const capabilities = registry.capabilities();
  assert.ok(Object.keys(capabilities.commands).length > 0);
  assert.ok(registry.robotDocs().includes("classifier"));
  assert.ok(registry.schema("gate").commands.gate);
});

test("committed decision contracts validate", async () => {
  // gate.json is legacy shape (no host/consumer) and is covered elsewhere;
  // full-shape contracts must validate here.
  for (const name of ["screen.json", "pin.json"]) {
    const raw = JSON.parse(
      await readFile(new URL(`../contracts/${name}`, import.meta.url), "utf8"),
    );
    assert.ok(validateContract(raw).family);
  }
});
