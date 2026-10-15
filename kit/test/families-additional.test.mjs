// Cohort-B adapter invariants, source-description scope only (jev-b35c.17.2).
//
// What exists in-tree: the family registry (capabilities/schema/validation)
// and full-shape decision contracts. What does NOT exist: any implementation
// of the seven adapter verbs (run, batch, explain, cases, eval, calibrate,
// watch) — FAMILY_VERBS is only a reserved-family-name blacklist, and adding
// `watch` there would forbid the cohort-B family NAMED watch, so the record
// is deliberately left at six words and guarded open below. Memory-enforcement
// live switch and effort shadow-only likewise have no executable subject.
// Those belong to jev-b35c.17.1 (open) or director routing.
// NO-CLAIM: this pins evidence-path invariants, not adapter behavior.
// No model calls, no network.

import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  createFamilyRegistry,
  validateFamilyNames,
} from "../src/families/registry.ts";
import { validateContract } from "../src/contracts.ts";

const familyNamed = (name) => [{ name, usage: "x", description: "x" }];

test("cohort-B watch family is not blocked by the verb record", () => {
  const errors = validateFamilyNames(familyNamed("watch"));
  assert.ok(
    errors.every((message) => !message.includes("reserved family name")),
    `family 'watch' must stay registrable; got: ${JSON.stringify(errors)}`,
  );
});

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
