/**
 * omp-jev-review — advisory review scorer for omp.
 *
 * WHY THIS ONE CALLS JEV, WHEN omp-jev-harm AND omp-jev-preaction DO NOT.
 * Those gates were measured against a live model and WON: four regexes beat Jev 12/12 to 11/12
 * at FP 0/38, so paying an API call per bash was a cost-benefit loss. That was a ruling about
 * ONE SURFACE, not a ban on the model.
 *
 * This surface is the opposite case. "Does this diff deserve review attention?" has no cheap
 * expression — there is no regex for `this refactor silently changed a default`. A judge earns
 * its seat exactly where a rule cannot be written, which is the premise of the lane.
 *
 * Upstream `jev-review` is RUN at 13/13 offline
 * (docs/demos/upstream-repro/jev-review-real-diffs-20260919.md).
 *
 * NEVER blocks. NEVER throws into the host. `tool_call` returns undefined on every path.
 * `tool_result` returns undefined except for one case: a diff it scored with boundary >=
 * BOUNDARY_COMMENT gets one advisory line appended to the git output (bead jev-k9z.2). It
 * carries no merge authority and says so.
 * A failed call records `review_error`, never a pass — NEGATIVE_EVIDENCE R40: a crashed
 * classifier recording a pass is indistinguishable from a clean result.
 */
import { execFile } from "node:child_process";
import { askJev } from "../../../kit/src/client.ts";

import { recording } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. Every Jev score it produces is
 * appended to the register instead of being discarded when the run ends.
 * The register stores a sha256 of the input and NEVER the input itself, and it is
 * not a cache: it records that a question was answered, it never answers one.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-review", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-review.decision.v1";
const DIAG = "com.zeststream.omp-jev-review.diagnostic.v1";

const MAX_DIFF = 12000;

/**
 * Questions only. The WIRE SHAPE lives in work/jev-client and nowhere else — this extension
 * hand-rolled its own fetch once and got HTTP 400 for inventing `{questions: [...], context}`.
 * If you need a shape the client does not support, extend the client and its tests.
 *
 * TWO questions, because measurement killed the third. `measure.mjs` scored all three against
 * seven diffs whose answers we know by construction. `scope` said **no** on every one of them,
 * including the 400-line rename sold as "tidy up" that it exists to catch (0.39, twice), and
 * scored that case BELOW a three-line auth deletion (0.43) — so it is not a threshold problem,
 * the ordering is wrong too. Its 6/7 was the base rate of a mostly-false label, not judgement.
 * A question whose verdict does not change with its input is noise with a confidence attached.
 */
const QUESTIONS = {
  behaviour: "Does this diff alter behaviour that an existing caller depends on?",
  boundary: "Does this diff touch a security, permission, or authentication boundary?",
};

/**
 * Deterministic applicability (bead jev-deep-kit-8q7.11, decided by pane 1
 * on the 686-commit draw): a diff is applicable iff it is not thin AND it
 * touches at least one code file. The extension set is derived from the
 * draw's file inventory (.md 608, .json 231, .sh 101, .mjs 85, .tsv 67,
 * .ts 38, .jsonl 28, .py 22, …) — the only executable/source extensions
 * observed there are .sh/.mjs/.ts/.py. This matched the noul gate on
 * 556/567 substantial diffs (98.1%), costs zero calls, and cannot flip on
 * wording. The 11 disagreements are listed in the draw receipt; 7 are
 * config/docs the gate scored (e.g. extensionless githooks/pre-commit,
 * package.json), 4 are code-mixed diffs the gate refused — all applicable
 * here. The Jev applicability question is retired for this tool (NO-CLAIM
 * in the bead); Jev still does the review scoring itself.
 */
/**
 * Thin diffs never reach Jev: fewer than 10 added+removed code lines, or no
 * `@@` hunks at all, is not worth a reviewer's (or a model's) attention.
 */
export function isThinDiff(diff: string): boolean {
  if (!/^@@ /m.test(diff)) return true;
  let changed = 0;
  for (const line of diff.split("\n")) {
    if (line.startsWith("+") && !line.startsWith("+++")) changed++;
    else if (line.startsWith("-") && !line.startsWith("---")) changed++;
    if (changed >= 10) return false;
  }
  return true;
}

const CODE_EXTENSIONS = [".ts", ".mjs", ".py", ".sh"];

export function touchesCodeFile(diff: string): boolean {
  return changedFiles(diff).some(isCodePath);
}

function isCodePath(path: string): boolean {
  return CODE_EXTENSIONS.some((ext) => path.endsWith(ext));
}

/**
 * Vendored, generated and lock files are not ours to review (bead jev-k9z.2 planted negative:
 * a 10k-line vendored diff must be applicable:false). A path is vendored when any directory
 * segment is one of these, or its basename is a lockfile.
 */
const VENDORED_SEGMENTS: Record<string, true> = {
  node_modules: true, vendor: true, third_party: true, dist: true, build: true, ".venv": true,
  venv: true, "site-packages": true, "docs-mirror": true, upstream: true,
};
const LOCKFILES: Record<string, true> = {
  "package-lock.json": true, "yarn.lock": true, "pnpm-lock.yaml": true, "bun.lock": true,
  "bun.lockb": true, "uv.lock": true, "Cargo.lock": true, "poetry.lock": true, "go.sum": true,
};

export function isVendoredPath(path: string): boolean {
  const parts = path.split("/");
  const base = parts[parts.length - 1] ?? "";
  return Object.hasOwn(LOCKFILES, base) || parts.slice(0, -1).some((p) => Object.hasOwn(VENDORED_SEGMENTS, p));
}

/** Post-image path of every file section, in order (`diff --git a/X b/Y` -> Y). */
export function changedFiles(diff: string): string[] {
  const files: string[] = [];
  for (const line of diff.split("\n")) {
    const m = /^diff --git a\/(.+) b\/(.+)$/.exec(line);
    if (m) files.push(m[2]);
  }
  return files;
}

/**
 * The diff with every vendored file section removed, and how many sections were dropped.
 * Text before the first `diff --git` header (a `git show` commit header) is kept.
 */
export function reviewableDiff(diff: string): { diff: string; dropped: number } {
  const sections = diff.split(/(?=^diff --git )/m);
  let dropped = 0;
  const kept = sections.filter((section) => {
    const m = /^diff --git a\/(.+) b\/(.+)$/m.exec(section);
    if (!m || !section.startsWith("diff --git ")) return true;
    if (isVendoredPath(m[2])) {
      dropped++;
      return false;
    }
    return true;
  });
  return { diff: kept.join(""), dropped };
}

/**
 * A scored boundary at or above this appends one advisory line to the git output. Chosen by
 * fire rate, not accuracy: on the 125 real code diffs the 686-commit draw scored
 * (docs/demos/upstream-repro/omp-jev-review-draw-20260923.md), boundary >= 0.9 fired on 3
 * (2.4%), >= 0.7 on 13. Whether those 3 are true boundary changes is unmeasured.
 */
export const BOUNDARY_COMMENT = 0.9;
const MAX_PENDING = 100;

/** A clean `git diff|show` argv, or null if the string is not safe to exec. */
export function gitArgv(command: string): string[] | null {
  if (/[;&|`$<>\\\n]/.test(command) || command.includes("$(")) return null;
  const tokens = command.trim().split(/\s+/).filter(Boolean);
  if (tokens.length < 2 || tokens[0] !== "git") return null;
  if (tokens[1] !== "diff" && tokens[1] !== "show") return null;
  return tokens;
}

type DiffRun = (argv: string[]) => Promise<string>;

const defaultDiffRun: DiffRun = (argv) =>
  new Promise((resolve, reject) => {
    execFile(argv[0], argv.slice(1), { timeout: 3000, maxBuffer: 200_000, encoding: "utf8" }, (err, stdout) => {
      if (err) reject(err);
      else resolve(stdout);
    });
  });

let diffRun: DiffRun = defaultDiffRun;

/** Tests inject a runner. Production uses execFile. Passing null restores the default. */
export function setDiffRunner(next: DiffRun | null): void {
  diffRun = next ?? defaultDiffRun;
}

export async function readDiff(command: string): Promise<{ ok: true; diff: string } | { ok: false; reason: string }> {
  const argv = gitArgv(command);
  if (!argv) return { ok: false, reason: "unsafe-command" };
  try {
    const stdout = await diffRun(argv);
    if (!stdout.trim()) return { ok: false, reason: "empty-diff" };
    return { ok: true, diff: stdout };
  } catch {
    return { ok: false, reason: "diff-exec" };
  }
}

type ToolCallEvent = { toolName?: unknown; name?: unknown; toolCallId?: unknown; input?: unknown; command?: unknown };
type ToolResultEvent = { toolName?: unknown; toolCallId?: unknown; content?: unknown; isError?: unknown };
type Host = {
  on: (event: string, handler: (event: any) => Promise<unknown>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};
export default function ompJevReview(pi: Host) {
  /** toolCallId -> boundary score, for diffs that earned the advisory line. */
  const pending = new Map<string, number>();

  pi.on("tool_result", async (event: ToolResultEvent) => {
    try {
      const id = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      if (id === null || !pending.has(id)) return undefined;
      const boundary = pending.get(id) as number;
      pending.delete(id);
      if (event?.toolName !== "bash" || event?.isError === true || !Array.isArray(event?.content)) {
        return undefined;
      }
      const note =
        `\n[jev-review advisory, no merge authority] boundary ${boundary.toFixed(2)}: this diff may ` +
        "touch a security, permission, or authentication boundary. Fires on about 2% of code diffs; " +
        "accuracy unmeasured.";
      return { content: [...event.content, { type: "text", text: note }] };
    } catch {
      return undefined;
    }
  });

  pi.on("tool_call", async (event: ToolCallEvent) => {
    try {
      const tool = String(event?.toolName ?? event?.name ?? "");
      const input = event?.input;
      const raw =
        (input && typeof input === "object" && "command" in input ? input.command : undefined) ??
        event?.command;
      const command = typeof raw === "string" ? raw : undefined;
      if (tool !== "bash" || command === undefined || !/\bgit\s+(diff|show)\b/.test(command)) {
        return undefined;
      }

      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      try {
        await pi.appendEntry(DIAG, {
          kind: "diff_command_observed",
          toolCallId,
          timestamp: new Date().toISOString(),
        });
      } catch {}
      const notApplicable = async (reason: string) => {
        try {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "review_not_applicable",
            applicable: false,
            command: command.slice(0, 2000),
            toolCallId,
            reason,
            timestamp: new Date().toISOString(),
          });
        } catch {
          /* observability must never break the session */
        }
        return undefined;
      };

      const loaded = await readDiff(command);
      // A command the extension will not re-run (a pipe, `&&`, a redirect) is out of scope, not a
      // failure: in the first 17 real fleet rows after the 2026-09-25 rollout, 9 were compound
      // commands such as `git add ... && git diff --cached`, and logging them as review_error made
      // most "errors" noise. A git that fails to run is still an error.
      if (!loaded.ok && loaded.reason === "unsafe-command") {
        return notApplicable("not-a-plain-diff-command");
      }
      if (!loaded.ok && loaded.reason !== "empty-diff") {
        try {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "review_error",
            command: command.slice(0, 2000),
            toolCallId,
            error: loaded.reason,
            failure: loaded.reason,
            timestamp: new Date().toISOString(),
          });
        } catch {}
        return undefined;
      }

      if (!loaded.ok) {
        return notApplicable("empty-diff");
      }
      const filtered = reviewableDiff(loaded.diff);
      if (filtered.dropped > 0 && !touchesCodeFile(filtered.diff) && touchesCodeFile(loaded.diff)) {
        return notApplicable("vendored-diff");
      }
      if (isThinDiff(filtered.diff)) {
        return notApplicable("thin-diff");
      }
      if (!touchesCodeFile(filtered.diff)) {
        return notApplicable("non-code-diff");
      }
      const result = await ask({
        state: { diff: filtered.diff.slice(0, MAX_DIFF) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      const boundary = probabilities?.boundary;
      const comment = toolCallId !== null && typeof boundary === "number" && boundary >= BOUNDARY_COMMENT;
      if (comment) {
        if (pending.size >= MAX_PENDING) pending.delete(pending.keys().next().value as string);
        pending.set(toolCallId as string, boundary as number);
      }

      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "review_scored" : "review_error",
          command: command.slice(0, 2000),
          toolCallId,
          ...(probabilities ? { probabilities, comment } : {}),
          ...(filtered.dropped > 0 ? { vendoredFilesDropped: filtered.dropped } : {}),
          ...(error === undefined ? {} : { error }),
          latencyMs: result.latencyMs,
          model: result.model,
          ...(result.ok ? {} : { failure: result.reason }),
          timestamp: new Date().toISOString(),
        });
      } catch {
        /* observability must never break the session */
      }
      return undefined;
    } catch {
      return undefined;
    }
  });
}
