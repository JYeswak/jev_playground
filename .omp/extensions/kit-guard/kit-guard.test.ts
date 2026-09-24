// W1.4 port of the kit's kit-guard.test.ts to the jev layout (bun test).
// Expectations are written from the repo layout (notes/deep/kit-guard-jev-cases.tsv),
// not from the new regex. Run: bun test ./.omp/extensions/kit-guard/kit-guard.test.ts
import { describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, writeFileSync, utimesSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import kitGuard, { projectRoot } from "./index";
import {
  bashVerdict,
  missingPatterns,
  pathVerdict,
  loadGuardConfig,
  validateGuardConfig,
  gatePathMatches,
  CONFIG_REL_PATH,
  FORBIDDEN_PATTERNS,
  type GuardConfig,
} from "./policy";

const cfg: GuardConfig = loadGuardConfig(process.cwd());

describe("config", () => {
  test("loads and names hookDir githooks", () => expect(cfg.hookDir).toBe("githooks"));
  test("lists its own path", () =>
    expect(cfg.gatePaths.some(p => p === ".omp/kit-guard.json")).toBe(true));
  test("covers the jev gate set", () => {
    for (const p of [
      "foundation/gates.sh",
      "githooks/*",
      ".git/hooks/*",
      ".omp/config.yml",
      ".omp/extensions/kit-guard/*",
    ]) {
      expect(cfg.gatePaths).toContain(p);
    }
    expect(cfg.gatePaths.some(p => p.includes("gates.d"))).toBe(true);
    expect(cfg.gatePaths.some(p => p.includes("kit-"))).toBe(true);
  });
  test("requires all 12 patterns", () => expect(cfg.requiredPatterns).toEqual([...FORBIDDEN_PATTERNS]));
  test("allows read-only git config", () =>
    expect(cfg.readOnlyBashAllow).toEqual(expect.arrayContaining(["git config --get", "git config --list"])));
});

// W1.3 layout table: notes/deep/kit-guard-jev-cases.tsv layout rows. 0 mismatches is the W1.4 oracle.
describe("W1.3 layout rows", () => {
  const rows: Array<[string, "bash" | "path", string]> = [
    ["block", "path", "githooks/pre-commit"],
    ["block", "bash", "rm githooks/commit-msg"],
    ["block", "bash", "chmod -x githooks/pre-commit"],
    ["block", "path", "foundation/gates.sh"],
    ["block", "path", "foundation/gates.d/44-native-surface.exemptions"],
    ["block", "bash", "git config core.hooksPath /dev/null"],
    ["block", "bash", "git commit --no-verify -m x"],
    ["pass", "bash", "git config --get core.hooksPath"],
    ["pass", "bash", "git config --list | grep hooksPath"],
    ["pass", "bash", 'git commit -m "document the -n flag"'],
    ["pass", "path", "upstream/typesafe-ai/skills/templates/x.md"],
    ["block", "path", ".omp/config.yml"],
    ["block", "path", ".omp/rules/kit-no-verify.md"],
    ["pass", "path", "notes/deep/x.md"],
  ];
  for (const [expectKw, kind, sample] of rows) {
    test(`${expectKw}: ${kind} ${sample}`, () => {
      const v = kind === "bash" ? bashVerdict(sample, cfg) : pathVerdict(sample, false, cfg);
      expect(v ? "block" : "pass").toBe(expectKw);
    });
  }
  test("self path is blocked without the flag", () =>
    expect(pathVerdict(".omp/kit-guard.json", false, cfg)?.block).toBe(true));
  test("self path is writable with KIT_GATE_EDIT=1", () =>
    expect(pathVerdict(".omp/kit-guard.json", true, cfg)).toBeNull());
});

describe("kit bash rules kept (jev-applicable)", () => {
  const blocked = [
    'git commit -m "wip" --no-verify',
    'git commit -nm "wip"',
    "git push origin main --no-verify",
    "git config core.hooksPath /dev/null",
    "git -c core.hooksPath=/tmp commit -m x",
    "git config --unset core.hooksPath",
    'git commit -n -m x',
    '[ -n "$x" ] && git commit -n -m "still a bypass" -- path',
    "rm .git/hooks/pre-commit",
    "echo 'exit 0' > foundation/gates.sh",
    "cat patch | tee foundation/kit/check-claim-discipline.sh",
  ];
  for (const c of blocked) test(`blocks: ${c}`, () => expect(bashVerdict(c, cfg)?.block).toBe(true));
  const allowed = [
    'git commit -m "feat: parser"',
    'git commit --amend -m "typo"',
    "git push -n origin main",
    "sh foundation/kit/check-claim-discipline.sh --selftest",
    "cat githooks/pre-commit",
    "br close bd-1 --reason 'cargo test -> 41 passed; commit abc1234'",
    '[ -n "$x" ] && git commit -m "msg" -- path',
  ];
  for (const c of allowed) test(`allows: ${c}`, () => expect(bashVerdict(c, cfg)).toBeNull());
  test("br close is NOT in bashVerdict (stays a TTSR rule)", () =>
    expect(bashVerdict("br close jev-x --reason done", cfg)).toBeNull());
});

describe("kit path rules kept (jev-applicable)", () => {
  for (const p of [
    "foundation/kit/check-claim-discipline.sh",
    "foundation/kit/check-readiness.sh",
    "githooks/pre-commit",
    ".git/hooks/pre-commit",
    "foundation/gates.d/10-fixture-integrity.sh",
    "/abs/proj/foundation/kit/check-claim-discipline.sh",
  ])
    test(`blocks ${p}`, () => expect(pathVerdict(p, false, cfg)?.block).toBe(true));
  for (const p of ["src/lib.rs", "docs/planning/packet.md", "AGENTS.md", "scripts/build.sh", "registries/claims.tsv"])
    test(`allows ${p}`, () => expect(pathVerdict(p, false, cfg)).toBeNull());
  test("KIT_GATE_EDIT override", () => expect(pathVerdict("foundation/gates.sh", true, cfg)).toBeNull());
});

describe("kit tests dropped (with reason)", () => {
  test("dropped bash: chmod -x .githooks/pre-commit — reason: dot-githooks does not exist here; hookDir is githooks (W1.3 rows cover githooks/)", () =>
    expect(true).toBe(true));
  test("dropped bash: echo > scripts/check-readiness.sh — reason: scripts/check-*.sh is not the jev gate path; foundation/kit/check-*.sh arm covers it", () =>
    expect(true).toBe(true));
  test("dropped bash: tee .github/workflows/kit-gates.yml — reason: no .github in this repo (plan App. A); foundation/gates.* arms cover the gate set", () =>
    expect(true).toBe(true));
  test("dropped path: scripts/check-readiness.sh — reason: same as above; replaced by foundation/kit/check-*.sh", () =>
    expect(true).toBe(true));
  test("dropped path: .githooks/pre-commit — reason: dot path absent; replaced by githooks/pre-commit", () =>
    expect(true).toBe(true));
  test("dropped path: .github/workflows/kit-gates.yml — reason: no .github here", () =>
    expect(true).toBe(true));
  test("dropped path: templates/agents.md — reason: over-broad (^|/)templates/ blocks vendored clones; W1.3 requires upstream/.../templates/x.md to PASS", () =>
    expect(true).toBe(true));
  test("dropped path: scripts/check-claim-discipline.sh — reason: jev path is foundation/kit/check-claim-discipline.sh (absolute arm kept)", () =>
    expect(true).toBe(true));
});

describe("fail-closed config", () => {
  test("missing dir throws", () => {
    const d = mkdtempSync(join(tmpdir(), "kitguard-nocfg-"));
    expect(() => loadGuardConfig(d)).toThrow();
  });
  test("malformed object throws", () => expect(() => validateGuardConfig({})).toThrow());
  test("config without its own path throws", () =>
    expect(() => validateGuardConfig({ ...cfg, gatePaths: ["foundation/gates.sh"] })).toThrow());
  test("bash blocks on malformed config", () =>
    expect(bashVerdict("echo hi", {})?.block).toBe(true));
  test("path blocks on malformed config", () =>
    expect(pathVerdict("notes/deep/x.md", false, {})?.block).toBe(true));
  test("gatePathMatches honors globs", () => {
    expect(gatePathMatches("foundation/gates.d/10-fixture-integrity.sh", cfg)).toBe(true);
    expect(gatePathMatches(".omp/rules/kit-close-needs-evidence.md", cfg)).toBe(true);
    expect(gatePathMatches("notes/deep/x.md", cfg)).toBe(false);
  });
});

describe("missingPatterns", () => {
  const full = FORBIDDEN_PATTERNS.map((p, i) => `${i + 1}. ${p} (x)`).join("\n");
  test("none missing", () => expect(missingPatterns(full, cfg)).toEqual([]));
  test("detects removal", () => expect(missingPatterns(full.replace("close-pump abuse", ""), cfg)).toEqual(["close-pump abuse"]));
});

// Drive the real extension entry point with a minimal fake ExtensionAPI.
// Each harness dir gets a copy of the repo guard config so loadGuardConfig(root)
// resolves there (fail-closed arm); session_start points the guard at that root.
function harness(cwd: string) {
  const handlers: Record<string, (...args: never[]) => unknown> = {};
  const sent: { content: string; opts: unknown }[] = [];
  const notified: string[] = [];
  mkdirSync(join(cwd, ".omp"), { recursive: true });
  writeFileSync(join(cwd, CONFIG_REL_PATH), JSON.stringify(cfg, null, 2));
  const pi = {
    setLabel() {},
    registerCommand() {},
    on(ev: string, fn: (...args: never[]) => unknown) {
      handlers[ev] = fn;
    },
    sendMessage(m: { content: string }, opts: unknown) {
      sent.push({ content: m.content, opts });
    },
  };
  kitGuard(pi as never);
  const ctx = { cwd, ui: { notify(msg: string) { notified.push(msg); } } };
  return { handlers, sent, notified, ctx };
}

describe("extension wiring", () => {
  const dir = mkdtempSync(join(tmpdir(), "kitguard-"));
  const agents = join(dir, "AGENTS.md");
  writeFileSync(agents, FORBIDDEN_PATTERNS.join("\n"));
  utimesSync(agents, new Date(1_000_000), new Date(1_000_000));
  const { handlers, sent, ctx } = harness(dir);

  test("session_start points the guard at the project root", async () => {
    await (handlers.session_start as (e: unknown, c: unknown) => Promise<void>)({}, ctx);
  });

  test("registers the five handlers", () =>
    expect(Object.keys(handlers).sort()).toEqual(["agent_end", "session_compact", "session_start", "tool_call", "tool_result"]));

  test("tool_call blocks --no-verify", async () => {
    const r = (await (handlers.tool_call as (e: unknown, c: unknown) => Promise<{ block?: boolean }>)(
      { toolName: "bash", input: { command: "git commit -m x --no-verify" } },
      ctx,
    )) as { block?: boolean } | undefined;
    expect(r?.block).toBe(true);
  });
  test("pure pathVerdict blocks gate edit without the flag", () =>
    expect(pathVerdict("foundation/gates.sh", false, cfg)?.block).toBe(true));
  test("tool_call allows normal write", async () => {
    const r = await (handlers.tool_call as (e: unknown, c: unknown) => unknown)(
      { toolName: "write", input: { path: "src/a.ts", content: "" } },
      ctx,
    );
    expect(r).toBeUndefined();
  });
  test("tool_result flags AGENTS.md pattern removal", async () => {
    writeFileSync(agents, FORBIDDEN_PATTERNS.filter(p => p !== "scope-splitting").join("\n"));
    const r = (await (handlers.tool_result as (e: unknown, c: unknown) => Promise<{ isError?: boolean; content?: unknown }>)(
      { toolName: "edit", input: { path: "AGENTS.md" }, content: [], isError: false },
      ctx,
    )) as { isError?: boolean; content?: unknown } | undefined;
    expect(r?.isError).toBe(true);
    expect(JSON.stringify(r?.content)).toContain("scope-splitting");
  });
  test("agent_end: silent when AGENTS.md unchanged", async () => {
    const n = sent.length;
    await (handlers.agent_end as () => Promise<void>)();
    expect(sent.length).toBe(n);
  });
  test("agent_end: re-read prompt when AGENTS.md edited externally", async () => {
    utimesSync(agents, new Date(), new Date(Date.now() + 5000));
    await (handlers.agent_end as () => Promise<void>)();
    expect(sent.at(-1)?.content).toContain("AGENTS.md changed on disk");
    expect(sent.at(-1)?.opts).toEqual({ deliverAs: "nextTurn" });
  });
  test("session_compact queues the re-anchor", async () => {
    await (handlers.session_compact as () => Promise<void>)();
    expect(sent.at(-1)?.content).toContain("context was just compacted");
  });
});

describe("launched from a subdirectory", () => {
  const dir = mkdtempSync(join(tmpdir(), "kitguard-root-"));
  mkdirSync(join(dir, ".git"));
  mkdirSync(join(dir, "src", "deep"), { recursive: true });
  writeFileSync(join(dir, "AGENTS.md"), FORBIDDEN_PATTERNS.filter(p => p !== "bench-path hardcoding").join("\n"));
  test("projectRoot walks up to .git", () => expect(projectRoot(join(dir, "src", "deep"))).toBe(dir));
  test("A9 check finds root AGENTS.md from subdir cwd", async () => {
    const h = harness(join(dir, "src", "deep"));
    await (h.handlers.session_start as (e: unknown, c: unknown) => Promise<void>)({}, h.ctx);
    const r = (await (h.handlers.tool_result as (e: unknown, c: unknown) => Promise<{ content?: unknown }>)(
      { toolName: "write", input: { path: "../../AGENTS.md" }, content: [], isError: false },
      h.ctx,
    )) as { content?: unknown } | undefined;
    expect(JSON.stringify(r?.content)).toContain("bench-path hardcoding");
  });
});
