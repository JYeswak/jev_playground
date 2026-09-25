// Guard regression inputs are commands-as-data. Never execute these git/settings strings.
// Run from the staged jev tree: bun test ./.omp/extensions/kit-guard/kit-guard.test.ts
import { afterAll, describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, utimesSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import kitGuard from "./index";
import {
  bashVerdict,
  missingPatterns,
  pathVerdict,
  loadGuardConfig,
  validateGuardConfig,
  CONFIG_REL_PATH,
  FORBIDDEN_PATTERNS,
} from "./policy";

const cfg = loadGuardConfig(import.meta.dir);
const scratchRoot = resolve(import.meta.dir, "../../..", "var/agent-tmp");
mkdirSync(scratchRoot, { recursive: true });
const scratch = mkdtempSync(join(scratchRoot, "kit-guard-test-"));
afterAll(() => rmSync(scratch, { recursive: true, force: true }));

const gitFailures: [string, string][] = [
  ["G1 long flag", "git commit -q --no-verify -m x"],
  ["G2 single-quoted flag", "git commit -q '--no-verify' -m x"],
  ["G3 double-quoted flag", 'git commit -q "--no-verify" -m x'],
  ["G4 quoted short flag", "git commit -q -m x '-n'"],
  ["G5 abbreviated flag", "git commit -q --no-veri -m x"],
  ["G6 lowercase hook key", "git -c core.hookspath=/dev/null commit -q -m x"],
  ["G7 quoted hook key", 'git -c "core.hooksPath=/dev/null" commit -q -m x'],
  ["G8 environment config", "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -q -m x"],
  ["G9 config mutation", "git config core.hookspath /dev/null && git commit -q -m x"],
  ["G10 command substitution", 'grep -q x "$(git commit -q --no-verify -m x)" /dev/null; true'],
  ["G11 backtick substitution", 'grep -q x "`git commit -q --no-verify -m x`" /dev/null; true'],
];

describe("B5 measured hook bypasses", () => {
  for (const [label, command] of gitFailures) {
    test(label, () => {
      expect(bashVerdict(command, cfg)?.block).toBe(true);
      expect(bashVerdict(command, cfg, true)?.block).toBe(true);
    });
  }
  for (const command of [
    "git commit -nm x",
    "git -C repo commit --no-veri -m x",
    'env git commit "--no-verify" -m x',
    'command /usr/bin/git commit --no-verify -m x',
    "git push origin main --no-verify",
    "git push origin main --no-veri",
    "git config --unset core.hookspath",
    "git config unset core.hooksPath",
    "git config set core.hooksPath /dev/null",
    'git -ccore.HOOKSPATH=/dev/null commit -m x',
    'git --config-env=core.hooksPath=HOOKS commit -m x',
    'env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hookspath GIT_CONFIG_VALUE_0=/dev/null git commit -m x',
    '[ -n "$x" ] && git commit -n -m x',
    "git commit -m 'read-only; message' --no-verify",
    "bash -c 'git commit --no-verify -m x'",
    'printf "%s" "$(printf "%s" "$(git commit --no-verify -m x)")"',
    "cat <(git commit --no-verify -m x)",
    "cat <<EOF\n$(git commit --no-verify -m x)\nEOF",
    "rm githooks/commit-msg",
    "chmod -x 'githooks/pre-commit'",
    "rm .git/hooks/pre-commit",
  ]) test(`blocks ${command}`, () => expect(bashVerdict(command, cfg, true)?.block).toBe(true));
});

describe("literal arguments and ordinary reads stay quiet", () => {
  for (const command of [
    "git commit -q -m x",
    'git commit -m "document the -n flag and --no-verify"',
    "git commit -m '--no-verify'",
    "git commit --message --no-verify",
    "git commit -mn",
    "git commit --file '-n'",
    "git commit -m x -- --no-verify",
    "git push -n origin main",
    "git push --dry-run origin main",
    '[ -n "$x" ] && git commit -m "msg" -- path',
    'test -n "$x"; git commit -m x',
    '[[ -n "$x" ]] && git commit -m x',
    "git config --get core.hooksPath",
    "git config --get-all core.hookspath",
    "git config core.hooksPath",
    "git config get core.hooksPath",
    "git config --list | grep hooksPath",
    "git config --list; git commit -m x",
    "git -c color.ui=false commit -m x",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=color.ui GIT_CONFIG_VALUE_0=false git commit -m x",
    "grep 'git commit --no-verify' README.md",
    'rg "git config core.hookspath /dev/null" README.md',
    "grep '$(git commit --no-verify -m x)' README.md",
    "grep '`git commit --no-verify -m x`' README.md",
    'echo "\\$(git commit --no-verify -m x)"',
    'printf "%s" "$(git config --get core.hooksPath)"',
    "cat <<'EOF'\ngit commit --no-verify -m x\n$(git commit --no-verify -m x)\nEOF",
    "cat <<EOF\ngit commit --no-verify -m x\nEOF",
    "# git commit --no-verify\ngit commit -m x",
    "cat githooks/pre-commit",
    "echo 'rm githooks/pre-commit'",
    "printf '%s' 'echo > foundation/gates.sh'",
    "sh foundation/kit/check-claim-discipline.sh --selftest",
    "br close bd-1 --reason 'cargo test -> 41 passed; commit abc1234'",
  ]) test(command, () => expect(bashVerdict(command, cfg)).toBeNull());
});

describe("heredoc execution context", () => {
  test("known shells execute heredoc stdin while literal consumers leave it as data", () => {
    const body = gitFailures[0][1];
    for (const shell of ["bash", "sh", "zsh", "dash", "ksh"]) {
      expect(bashVerdict(`${shell} <<'EOF'\n${body}\nEOF`, cfg, true)).toMatchObject({ block: true });
      expect(bashVerdict(`${shell} <<EOF\n${body}\nEOF`, cfg, true)).toMatchObject({ block: true });
    }
    for (const reader of ["cat", "python", "bash -n", "bash script.sh", "bash -c 'cat'"]) {
      expect(bashVerdict(`${reader} <<'EOF'\n${body}\nEOF`, cfg)).toBeNull();
    }
    expect(bashVerdict(`bash -s arg <<-'EOF'\n\t${body}\n\tEOF`, cfg, true)).toMatchObject({ block: true });
    expect(bashVerdict("bash <<'EOF'\ngit config --get core.hooksPath\nEOF", cfg)).toBeNull();
    expect(bashVerdict(`cat <<'EOF'\n$(${body})\nEOF`, cfg)).toBeNull();
  });

  test("parent expansions and child-shell expansions retain their respective execution scope", () => {
    const body = gitFailures[0][1];
    expect(bashVerdict(`cat <<EOF\n'$(${body})'\nEOF`, cfg, true)).toMatchObject({ block: true });
    expect(bashVerdict(`bash <<EOF\n\\$(${body})\nEOF`, cfg, true)).toMatchObject({ block: true });
    expect(bashVerdict(`cat <<EOF\n\\$(${body})\nEOF`, cfg)).toBeNull();
    expect(bashVerdict(`bash <<'OLD' <<'NEW'\n${body}\nOLD\nprintf safe\nNEW`, cfg)).toBeNull();
  });
});

describe("bounded shell analysis", () => {
  const nest = (command: string, depth: number) => "echo $(".repeat(depth) + command + ")".repeat(depth);
  const shell = (command: string) => "bash -c '" + command.replaceAll("'", "'\\''") + "'";

  test("excessive substitution and shell-body nesting returns a fail-closed decision", () => {
    const substitutions = nest("printf safe", 256);
    let mixed = nest("printf safe", 60);
    for (let i = 0; i < 8; i++) mixed = shell(mixed);
    for (const command of [substitutions, mixed]) {
      expect(bashVerdict(command, cfg)).toMatchObject({ block: true });
      expect(bashVerdict(command, cfg, true)).toMatchObject({ block: true });
    }
  });

  test("ordinary nesting preserves quiet reads and hook-bypass refusal", () => {
    expect(bashVerdict("echo >(echo x)", cfg)).toBeNull();
    expect(bashVerdict(shell(nest("git config --get core.hooksPath", 3)), cfg)).toBeNull();
    expect(bashVerdict(shell(nest(gitFailures[0][1], 3)), cfg, true)).toMatchObject({ block: true });
  });
});

const settingsFailures = [
  "omp config set ttsr.enabled false",
  "omp config set 'ttsr.enabled' false",
  'omp config set "ttsr.enabled" false',
  "omp --profile jev-lab config set disabledProviders '[\"agents\"]'",
  "omp --profile=jev-lab config reset ttsr.repeatGap",
  "omp config unset discovery.agents",
  "omp config set extensions '[]'",
  "omp config set disabledExtensions '[]'",
  "omp config set enabledProviders '[]'",
  'rg -q x "$(omp config set ttsr.enabled false)" /dev/null; true',
  'rg -q x "`omp config set ttsr.enabled false`" /dev/null; true',
  // No HOME-shaped exemption: inherited selectors and filesystem isolation are unproven.
  "HOME=/tmp/omp-home omp config set ttsr.enabled false",
  "HOME=/tmp/omp-home env -u HOME omp config set ttsr.enabled false",
  "HOME=/tmp/omp-home env HOME=/Users/josh omp config set ttsr.enabled false",
  "HOME=/tmp/omp-home HOME=/Users/josh omp config set ttsr.enabled false",
  "KIT_GATE_EDIT=1 omp config set ttsr.enabled false",
];

describe("B7 protected settings", () => {
  for (const command of settingsFailures) test(command, () => {
    expect(bashVerdict(command, cfg)?.block).toBe(true);
    expect(bashVerdict(command, cfg, true)).toBeNull();
  });
  for (const command of [
    "omp config get ttsr.enabled",
    "omp --profile jev-lab config list",
    "omp config set theme.dark titanium",
    "omp config set models.default example",
    "omp config set ttsrExample false",
    "rg 'omp config set ttsr.enabled false' README.md",
    "rg '$(omp config set ttsr.enabled false)' README.md",
    "echo 'omp config set disabledProviders []'",
  ]) test(`quiet ${command}`, () => expect(bashVerdict(command, cfg)).toBeNull());
  for (const path of [
    "cfg://ttsr/repeatGap", "cfg://TTSR.enabled/save", "CFG://TtSr/Enabled/SAVE",
    "cfg://extensions/save", "cfg://DISABLEDPROVIDERS", "cfg://enabledProviders/save",
    "cfg://discovery/agents", "cfg://disabledExtensions/save",
  ]) test(path, () => {
    expect(pathVerdict(path, false, cfg)?.block).toBe(true);
    expect(pathVerdict(path, true, cfg)).toBeNull();
  });
  for (const path of [
    "cfg://theme/dark", "cfg://models/default/save", "cfg://ttsrExample/save",
    "~/.omp/agent/config.yml", "/Users/josh/.omp/profiles/claude/agent/config.yml",
  ]) test(`outside field-aware scope ${path}`, () => expect(pathVerdict(path, false, cfg)).toBeNull());
});

describe("B7 gate-file protection", () => {
  for (const path of [
    "githooks/pre-commit", ".git/hooks/pre-commit", "foundation/gates.sh",
    "foundation/gates.d/44-native-surface.exemptions", "foundation/kit/check-readiness.sh",
    "/abs/proj/foundation/kit/check-claim-discipline.sh", ".omp/config.yml",
    ".omp/rules/kit-no-verify.md", ".omp/extensions/kit-guard/policy.ts", ".omp/kit-guard.json",
  ]) test(path, () => {
    expect(pathVerdict(path, false, cfg)?.block).toBe(true);
    expect(pathVerdict(path, true, cfg)).toBeNull();
  });
  for (const command of [
    "echo 'exit 0' > foundation/gates.sh",
    "cat patch | tee 'foundation/kit/check-claim-discipline.sh'",
    'echo patch >> "foundation/gates.d/44-native-surface.exemptions"',
    "tee notes/x.md githooks/pre-commit",
  ]) test(command, () => {
    expect(bashVerdict(command, cfg)?.block).toBe(true);
    expect(bashVerdict(command, cfg, true)).toBeNull();
  });
  for (const path of ["src/lib.rs", "notes/deep/x.md", "AGENTS.md", "upstream/typesafe-ai/skills/templates/x.md"])
    test(`ordinary file ${path}`, () => expect(pathVerdict(path, false, cfg)).toBeNull());
});

describe("fail-closed configuration and required patterns", () => {
  test("missing gate self-protection is invalid", () => {
    expect(() => validateGuardConfig({ ...cfg, gatePaths: ["foundation/gates.sh"] })).toThrow();
  });
  test("missing required pattern is invalid", () => {
    expect(() => validateGuardConfig({ ...cfg, requiredPatterns: cfg.requiredPatterns.slice(1) })).toThrow();
  });
  test("malformed config blocks even authorized mutations", () => {
    expect(bashVerdict("echo hi", {}, true)?.block).toBe(true);
    expect(pathVerdict("src/a.ts", true, {})?.block).toBe(true);
  });
  test("malformed config file fails closed", () => {
    const dir = mkdtempSync(join(scratch, "malformed-"));
    mkdirSync(join(dir, ".omp"));
    writeFileSync(join(dir, CONFIG_REL_PATH), "{");
    expect(() => loadGuardConfig(dir)).toThrow();
  });
  test("reports deleted forbidden patterns without rejecting intact AGENTS", () => {
    const full = FORBIDDEN_PATTERNS.join("\n");
    expect(missingPatterns(full, cfg)).toEqual([]);
    expect(missingPatterns(full.replace("close-pump abuse", ""), cfg)).toEqual(["close-pump abuse"]);
  });
});

// Drive consumer-visible decisions, not handler names or copies of config defaults.
function harness(authorized = false, subdir = "") {
  const cwd = mkdtempSync(join(scratch, "adapter-"));
  mkdirSync(join(cwd, ".git"));
  mkdirSync(join(cwd, ".omp"));
  writeFileSync(join(cwd, CONFIG_REL_PATH), JSON.stringify(cfg));
  const handlers: Record<string, (event: unknown, ctx: unknown) => unknown> = {};
  const sent: {
    message: { customType: string; content: string; display: boolean };
    options: { deliverAs: string };
  }[] = [];
  const pi = {
    setLabel() {}, registerCommand() {},
    sendMessage(message: (typeof sent)[number]["message"], options: (typeof sent)[number]["options"]) {
      sent.push({ message, options });
    },
    on(name: string, handler: (event: unknown, ctx: unknown) => unknown) { handlers[name] = handler; },
  };
  const previous = process.env.KIT_GATE_EDIT;
  try {
    if (authorized) process.env.KIT_GATE_EDIT = "1";
    else delete process.env.KIT_GATE_EDIT;
    kitGuard(pi as never);
  } finally {
    if (previous === undefined) delete process.env.KIT_GATE_EDIT;
    else process.env.KIT_GATE_EDIT = previous;
  }
  const ctx = { cwd: join(cwd, subdir), ui: { notify() {} } };
  mkdirSync(ctx.cwd, { recursive: true });
  return {
    cwd,
    sent,
    start: () => handlers.session_start({}, ctx),
    call: (toolName: string, input: unknown) => handlers.tool_call({ toolName, input }, ctx),
    result: (path: string) => handlers.tool_result({ toolName: "edit", input: { path }, content: [], isError: false }, ctx),
    end: () => handlers.agent_end({}, ctx),
    compact: () => handlers.session_compact({}, ctx),
  };
}

describe("extension decision boundary", () => {
  test("B7 captures process authorization; B5 cannot be authorized away", async () => {
    for (const authorized of [false, true]) {
      const h = harness(authorized);
      await h.start();
      expect(await h.call("bash", { command: "git commit '--no-verify' -m x" })).toMatchObject({ block: true });
      const settings = await h.call("bash", { command: "omp config set ttsr.enabled false" });
      const path = await h.call("write", { path: "cfg://TTSR/Enabled/save", content: "false" });
      const gate = await h.call("edit", { path: "foundation/gates.sh" });
      if (authorized) {
        expect(settings).toBeUndefined();
        expect(path).toBeUndefined();
        expect(gate).toBeUndefined();
      } else {
        expect(settings).toMatchObject({ block: true });
        expect(path).toMatchObject({ block: true });
        expect(gate).toMatchObject({ block: true });
      }
    }
  });
  test("read tools and model settings are outside protected mutation scope", async () => {
    const h = harness();
    await h.start();
    expect(await h.call("read", { path: "cfg://ttsr" })).toBeUndefined();
    expect(await h.call("write", { path: "cfg://models/default/save", content: "example" })).toBeUndefined();
    expect(await h.call("bash", { command: "omp config get ttsr.enabled" })).toBeUndefined();
    expect(await h.call("write", { path: "src/a.ts", content: "" })).toBeUndefined();
    expect(await h.call("edit", { edits: [{ path: "src/a.ts" }, { path: "cfg://extensions/save" }] })).toMatchObject({ block: true });
  });
  test("invalid project config blocks through the adapter", async () => {
    const h = harness(true);
    await h.start();
    writeFileSync(join(h.cwd, CONFIG_REL_PATH), "{}");
    expect(await h.call("bash", { command: "echo hi" })).toMatchObject({ block: true });
  });
  test("AGENTS deletion reports the missing pattern and intact content stays quiet", async () => {
    const h = harness();
    await h.start();
    const agents = join(h.cwd, "AGENTS.md");
    writeFileSync(agents, FORBIDDEN_PATTERNS.join("\n"));
    expect(await h.result("AGENTS.md")).toBeUndefined();
    writeFileSync(agents, FORBIDDEN_PATTERNS.filter(p => p !== "scope-splitting").join("\n"));
    expect(await h.result("AGENTS.md")).toMatchObject({ isError: true });
  });

  test("subdirectory sessions check the root policy rather than a nested or process-cwd copy", async () => {
    const h = harness(false, "src/deep");
    writeFileSync(join(h.cwd, "AGENTS.md"), FORBIDDEN_PATTERNS.filter(p => p !== "bench-path hardcoding").join("\n"));
    await h.start();
    expect(await h.call("write", { path: "ordinary.txt", content: "" })).toBeUndefined();
    const result = await h.result("../../AGENTS.md");
    expect(result).toMatchObject({ isError: true });
    expect(JSON.stringify(result)).toContain("bench-path hardcoding");
  });

  test("external policy edits notify once; unchanged and agent-acknowledged versions do not", async () => {
    const h = harness();
    const agents = join(h.cwd, "AGENTS.md");
    writeFileSync(agents, FORBIDDEN_PATTERNS.join("\n"));
    const initial = new Date("2026-01-01T00:00:00Z");
    const changed = new Date("2026-01-01T00:00:10Z");
    const acknowledged = new Date("2026-01-01T00:00:20Z");
    utimesSync(agents, initial, initial);
    await h.start();
    await h.end();
    expect(h.sent).toEqual([]);

    utimesSync(agents, changed, changed);
    await h.end();
    expect(h.sent).toHaveLength(1);
    const notification = h.sent[0];
    expect(notification).toMatchObject({
      message: { customType: "kit-guard", display: true },
      options: { deliverAs: "nextTurn" },
    });
    expect(notification.message.content).toContain(changed.toISOString());
    await h.end();
    expect(h.sent).toEqual([notification]);

    utimesSync(agents, acknowledged, acknowledged);
    expect(await h.result("AGENTS.md")).toBeUndefined();
    await h.end();
    expect(h.sent).toEqual([notification]);
  });

  test("compaction schedules the current project reanchor files, not a stale configuration", async () => {
    const h = harness();
    await h.start();
    const config = join(h.cwd, CONFIG_REL_PATH);
    writeFileSync(config, JSON.stringify({ ...cfg, reanchorFiles: ["policy/previous.md"] }));
    await h.compact();
    expect(h.sent).toHaveLength(1);
    expect(h.sent[0].message.content).toContain("policy/previous.md");

    writeFileSync(config, JSON.stringify({ ...cfg, reanchorFiles: ["policy/current.md", "policy/acceptance.md"] }));
    await h.compact();
    expect(h.sent).toHaveLength(2);
    expect(h.sent[1]).toMatchObject({
      message: { customType: "kit-guard", display: true },
      options: { deliverAs: "nextTurn" },
    });
    expect(h.sent[1].message.content).toContain("policy/current.md");
    expect(h.sent[1].message.content).toContain("policy/acceptance.md");
    expect(h.sent[1].message.content).not.toContain("policy/previous.md");
  });
});
