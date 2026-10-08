import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const api = await import("../src/contracts.ts").catch(() => null);

const fixture = async (name) => JSON.parse(await readFile(new URL(`../contracts/fixtures/${name}`, import.meta.url), "utf8"));

test("contract schema validator is available", () => {
  assert.equal(typeof api?.validateContract, "function", "kit/src/contracts.ts must export validateContract");
});

if (api?.validateContract) {
  test("gate and screen fixture contracts validate", async () => {
    for (const [name, family] of [["gate-refuse.json", "conformance-command-gate"], ["screen-pass.json", "conformance-result-screen"]]) {
      assert.equal(api.validateContract(await fixture(name)).family, family);
    }
    const actualScreen = JSON.parse(await readFile(new URL("../contracts/screen.json", import.meta.url), "utf8"));
    assert.equal(api.validateContract(actualScreen).family, "tool-result-injection-screen");
  });

  test("screen contracts cannot declare fail-closed safe side", async () => {
    const screen = await fixture("screen-pass.json");
    assert.throws(() => api.validateContract({ ...screen, safe_side: "refuse" }), (error) => String(error).toLowerCase().includes("safe_side") || String(error).toLowerCase().includes("surface"));
  });

  test("host and consumer are required contract owners", async () => {
    const gate = await fixture("gate-refuse.json");
    for (const field of ["host", "consumer"]) {
      const missing = { ...gate };
      delete missing[field];
      assert.throws(() => api.validateContract(missing), (error) => String(error).includes(field));
    }
  });

  test("command-gate cap refusal needs committed never-reached evidence", async () => {
    const gate = await fixture("gate-refuse.json");
    const capRefusal = {
      ...gate,
      budget: { ...gate.budget, cap_reached_action: "refuse" },
    };
    assert.throws(() => api.validateContract(capRefusal), (error) => ["cap", "never-reached", "evidence"].some((term) => String(error).toLowerCase().includes(term)));
  });
}
