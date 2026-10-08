import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const INVENTORY = resolve(ROOT, "work/jev-m35c/REGEX-INVENTORY.md");
const EXPECTED_REVIEW_EXPRESSIONS = 16;
const WATCHDOG_MS = 1_200;

if (!isMainThread) {
  try {
    const regex = new RegExp(workerData.source, workerData.flags);
    const started = performance.now();
    const matched = regex.test(workerData.input);
    parentPort.postMessage({ elapsedMs: performance.now() - started, matched });
  } catch (error) {
    parentPort.postMessage({ error: error.message });
  }
} else {
  function inventoryReferences() {
    const rows = readFileSync(INVENTORY, "utf8").split(/\r?\n/)
      .filter((line) => line.startsWith("|"))
      .filter((line) => line.includes("`HIGH-REVIEW`") || line.includes("`PROBE`"));

    return rows.flatMap((row) => {
      const columns = row.split("|").map((column) => column.trim());
      const reference = columns[1].match(/^`([^`]+)`$/)?.[1];
      assert.ok(reference, `missing source reference in inventory row: ${row}`);
      const match = reference.match(/^(.*):(\d+)(?:-(\d+))?$/);
      assert.ok(match, `invalid source reference: ${reference}`);
      const first = Number(match[2]);
      const last = Number(match[3] ?? match[2]);
      return Array.from({ length: last - first + 1 }, (_, offset) => ({
        path: match[1],
        line: first + offset,
        verdict: columns.filter(Boolean).at(-1).startsWith("`HIGH-REVIEW`") ? "HIGH-REVIEW" : "PROBE",
      }));
    });
  }

  function yamlCondition(line, reference) {
    const trimmed = line.trim();
    const value = trimmed.startsWith("condition:")
      ? trimmed.slice("condition:".length).trim()
      : trimmed.startsWith("-")
        ? trimmed.slice(1).trim()
        : undefined;
    assert.ok(value?.startsWith("'") && value.endsWith("'"), `unsupported TTSR condition at ${reference}`);

    let source = value.slice(1, -1).replaceAll("''", "'");
    let flags = "";
    if (source.startsWith("(?i)")) {
      source = source.slice(4);
      flags = "i";
    }
    return { source, flags };
  }

  function jsRegexLiteral(line, reference) {
    const start = line.indexOf("= /");
    assert.notEqual(start, -1, `missing JS regex literal at ${reference}`);
    let inClass = false;
    let escaped = false;
    let end = -1;
    for (let index = start + 3; index < line.length; index += 1) {
      const character = line[index];
      if (escaped) {
        escaped = false;
      } else if (character === "\\") {
        escaped = true;
      } else if (character === "[") {
        inClass = true;
      } else if (character === "]") {
        inClass = false;
      } else if (character === "/" && !inClass) {
        end = index;
        break;
      }
    }
    assert.notEqual(end, -1, `unterminated JS regex literal at ${reference}`);
    return { source: line.slice(start + 3, end), flags: line.slice(end + 1).match(/^[a-z]*/)?.[0] ?? "" };
  }

  function loadExpressions() {
    return inventoryReferences().map((reference) => {
      const sourcePath = resolve(ROOT, reference.path);
      const line = readFileSync(sourcePath, "utf8").split(/\r?\n/)[reference.line - 1];
      assert.ok(line, `missing source line ${reference.path}:${reference.line}`);
      const pattern = reference.path.endsWith(".md")
        ? yamlCondition(line, `${reference.path}:${reference.line}`)
        : jsRegexLiteral(line, `${reference.path}:${reference.line}`);
      new RegExp(pattern.source, pattern.flags);
      return { ...reference, ...pattern, id: `${reference.path}:${reference.line}` };
    });
  }

  function fit(length, prefix, suffix = "") {
    assert.ok(prefix.length + suffix.length <= length, "near-miss template exceeds requested length");
    return prefix + "x".repeat(length - prefix.length - suffix.length) + suffix;
  }

  function nearMiss(expression, length) {
    const { path, line } = expression;
    if (path.endsWith("kit-close-needs-evidence.md")) {
      return line === 4
        ? fit(length, "br close ")
        : fit(length, "br close ", " --reason=\"");
    }
    if (path.endsWith("kit-jsonl-close.md")) {
      return fit(length, '{"status":"closed","close_reason":"');
    }
    if (path.endsWith("kit-no-verify.md")) {
      const prefix = line >= 18 ? "GIT_CONFIG_COUNT=1 " : line === 17 ? "git -c " : line >= 15 ? "git config " : line === 14 ? "git push " : "git commit ";
      return fit(length, prefix);
    }
    if (path.endsWith("bash-callsite-grep-exclusion.md")) return fit(length, "grep ");
    if (path.endsWith("bash-glob-silenced.md")) return fit(length, "grep ", "*");
    if (path.endsWith("bash-pipe-exit.md")) return fit(length, "| head ", ";");
    if (path.endsWith("scorer-reimplementation.md")) return fit(length, "def ", "_");
    if (path.endsWith("jev-web-search-rerank.ts")) {
      const block = "[1] title\n https: x\n";
      return block.repeat(Math.ceil(length / block.length)).slice(0, length);
    }
    throw new Error(`no near-miss template for ${expression.id}`);
  }

  function runOne(source, flags, input) {
    return new Promise((resolveResult, reject) => {
      const worker = new Worker(new URL(import.meta.url), { workerData: { source, flags, input } });
      let settled = false;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolveResult(result);
      };
      const timer = setTimeout(() => {
        void worker.terminate();
        finish({ timedOut: true });
      }, WATCHDOG_MS);
      worker.once("message", (result) => {
        if (result.error) finish({ error: result.error });
        else finish(result);
      });
      worker.once("error", reject);
      worker.once("exit", (code) => {
        if (!settled && code !== 0) finish({ error: `worker exited ${code}` });
      });
    });
  }

  function median(values) {
    const sorted = [...values].sort((left, right) => left - right);
    return sorted[Math.floor(sorted.length / 2)];
  }

  const expressions = loadExpressions();

  test("inventory exposes all 16 HIGH-REVIEW and PROBE expressions from source lines", () => {
    assert.equal(expressions.length, EXPECTED_REVIEW_EXPRESSIONS);
    assert.equal(new Set(expressions.map(({ id }) => id)).size, EXPECTED_REVIEW_EXPRESSIONS);
    assert.equal(expressions.filter(({ verdict }) => verdict === "HIGH-REVIEW").length, 11);
    assert.equal(expressions.filter(({ verdict }) => verdict === "PROBE").length, 5);
  });

  test("measures source expressions on 5k and 50k near-misses with a killable watchdog", async () => {
    const results = [];
    for (const expression of expressions) {
      for (const length of [5_000, 50_000]) {
        const input = nearMiss(expression, length);
        assert.equal(input.length, length, `wrong near-miss size for ${expression.id}`);
        const samples = [];
        for (let attempt = 0; attempt < 3; attempt += 1) {
          const sample = await runOne(expression.source, expression.flags, input);
          assert.equal(sample.error, undefined, `could not measure ${expression.id}: ${sample.error}`);
          if (!sample.timedOut) assert.equal(sample.matched, false, `near-miss unexpectedly matched ${expression.id}`);
          samples.push(sample);
        }
        const timeouts = samples.filter(({ timedOut }) => timedOut).length;
        const values = samples.filter(({ elapsedMs }) => Number.isFinite(elapsedMs)).map(({ elapsedMs }) => elapsedMs);
        const medianMs = timeouts >= 2 ? null : median(values);
        results.push({ id: expression.id, verdict: expression.verdict, chars: length, medianMs, timedOutRuns: timeouts });
      }
    }

    console.log(`redos-timing ${JSON.stringify(results)}`);
    assert.equal(results.length, EXPECTED_REVIEW_EXPRESSIONS * 2);
  });

  test("the watchdog reports the planted nested-quantifier near-miss as slow", async () => {
    const sample = await runOne("(a+)+$", "", `${"a".repeat(30)}!`);
    assert.equal(sample.error, undefined);
    assert.ok(sample.timedOut || sample.elapsedMs > 1_000, "planted catastrophic pattern was not detected as >1s or timed out");
  });
}
