import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

describe("jev-candidate-check", () => {
  it("selftest: historical cases gate correctly (memory/V3/V5 STOP, retry PILOT, webscreen/gate GO)", () => {
    const r = spawnSync("python3", ["scripts/jev-candidate-check.py", "--selftest"], {
      encoding: "utf8",
      timeout: 120000,
    });
    assert.equal(r.status, 0, (r.stdout || "") + (r.stderr || ""));
    assert.match(r.stdout || "", /memory-keep: got STOP/);
    assert.match(r.stdout || "", /gate-cascade: got GO/);
  });

  it("flags the memory-D2 candidate STOP and pilots retry-flip", () => {
    for (const [file, want] of [
      ["work/jev-science/candidates/memory-D2.json", /^STOP memory-D2-topk/],
      ["work/jev-science/candidates/retry-flip.json", /^PILOT retry-flip/],
    ]) {
      const r = spawnSync("python3", ["scripts/jev-candidate-check.py", file], {
        encoding: "utf8",
        timeout: 60000,
      });
      assert.equal(r.status, 0, file + (r.stderr || ""));
      const last = (r.stdout || "").trim().split("\n").at(-1);
      assert.match(last, want, file);
    }
  });
});
