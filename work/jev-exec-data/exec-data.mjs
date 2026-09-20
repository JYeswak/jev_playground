/**
 * Executed-vs-data string distinguisher (R44 NEW TRIGGER).
 *
 * Problem: after the positional fix, all surviving organic fires are probe
 * commands shaped like `node -e "... 'some dangerous command' ..."` — the
 * dangerous text is a STRING LITERAL inside a `-e` program, passed as data
 * (object field, test argument, print comparison), never executed.
 *
 * Rule (narrow, testable): a trigger occurrence is DATA iff
 *   (1) it sits inside a string literal, AND
 *   (2) that literal sits inside an interpreter `-e`/`-c` program span, AND
 *   (3) the literal is NOT an argument to an exec-family call.
 * A fire is suppressed iff EVERY trigger occurrence in the command is data.
 * Anything else (unquoted trigger, trigger outside program spans, literal fed
 * to exec/execSync/execFile/spawn/system/popen/eval) stands.
 *
 * Deliberately textual, not a real parser: shells nest quotes arbitrarily and a
 * full parse is a bigger unit. The approximation is stated, with its boundary
 * (nested same-quote escapes, multi-line program spans) in exec-data.test.mjs.
 *
 * Does NOT touch rules-v4.mjs or harm-rule.ts (%71's ground).
 */

const EXEC_FAMILY = new Set([
  'exec', 'execSync', 'execFile', 'execFileSync', 'execa', 'spawn', 'spawnSync',
  'system', 'popen', 'eval', 'shell', 'runSync',
]);

// Interpreter program flags whose argument IS program text (not data).
const PROGRAM_FLAGS = ['-e', '-c', '--expression'];

// Find spans of `-e '...'` / `-c "..."` program text. The body runs to the
// MATCHING close quote, skipping over nested spans opened by other quote types
// (`-e "use('x')"` — inner singles do not end the body). Backslash escapes
// respected. Returns [{start, end}] in command coordinates.
export function programSpans(command) {
  const spans = [];
  const head = /(node|python3?|perl|ruby)\s+((?:\S+\s+)*?)(-e|-c|--expression)\s*(['"])/g;
  let m;
  while ((m = head.exec(command)) !== null) {
    const quote = m[4];
    let pos = m.index + m[0].length;
    const stack = [quote];
    while (pos < command.length && stack.length) {
      const ch = command[pos];
      if (ch === '\\') { pos += 2; continue; }
      if (ch === stack[stack.length - 1]) stack.pop();
      else if (ch === "'" || ch === '"' || ch === '`') stack.push(ch);
      pos++;
    }
    if (stack.length) continue; // unterminated: skip, fail-closed elsewhere
    const bodyStart = m.index + m[0].length;
    const bodyEnd = pos - 1;
    spans.push({ start: bodyStart, end: bodyEnd, body: command.slice(bodyStart, bodyEnd) });
  }
  return spans;
}

// String literals inside a program body: [{start, end}] in BODY coordinates.
function literalsIn(body) {
  const out = [];
  const re = /'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    const inner = m[1] ?? m[2] ?? m[3];
    const quote = m[0][0];
    const innerStart = m.index + 1;
    out.push({ start: innerStart, end: innerStart + inner.length, qstart: m.index, quote, text: inner });
  }
  return out;
}

// Nearest `name(` to the left of pos whose paren depth contains pos, or null.
// Depth computed over body[0..pos] counting ( and ) outside strings is overkill;
// heuristic: scan left for `identifier(` with balanced parens after it.
function enclosingCall(body, pos) {
  const before = body.slice(0, pos);
  const calls = [...before.matchAll(/([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\($/g)];
  // Walk back through candidate call opens; take the last one whose parens balance.
  for (let i = calls.length - 1; i >= 0; i--) {
    const m = calls[i];
    const openIdx = m.index + m[0].length - 1;
    let depth = 0;
    let inStr = null;
    for (let j = openIdx; j < pos; j++) {
      const ch = body[j];
      if (inStr) {
        if (ch === '\\') { j++; continue; }
        if (ch === inStr) inStr = null;
      } else if (ch === "'" || ch === '"' || ch === '`') inStr = ch;
      else if (ch === '(') depth++;
      else if (ch === ')') depth--;
    }
    if (depth > 0) {
      const full = m[1];
      return full.split('.').pop();
    }
  }
  return null;
}
/**
 * Blank every string literal inside `-e`/`-c` program spans that is NOT fed
 * to an exec-family call (spaces preserve coordinates). Returns the blanked
 * command plus whether anything was blanked.
 */
export function blankDataLiterals(command) {
  const spans = programSpans(command);
  if (!spans.length) return { blanked: command, blankedAny: false };
  const chars = [...command];
  let blankedAny = false;
  for (const span of spans) {
    for (const lit of literalsIn(span.body)) {
      const callee = enclosingCall(span.body, lit.qstart);
      if (callee && EXEC_FAMILY.has(callee)) continue; // exec-fed: keep
      for (let i = span.start + lit.start; i < span.start + lit.end; i++) {
        if (chars[i] !== '\n') chars[i] = ' ';
      }
      blankedAny = true;
    }
  }
  return { blanked: chars.join(''), blankedAny };
}

/**
 * Should a harm fire on `command` be suppressed? Blank all data-literals and
 * re-score with `firesFn` (async (cmd) => bool, the SHIPPED rule — no pattern
 * duplication anywhere in this file). Suppress iff the blanked command stops
 * firing: every trigger lived inside a data-literal. Anything else stands
 * (fail-closed toward firing).
 */
export async function suppressFire(command, firesFn) {
  const { blanked, blankedAny } = blankDataLiterals(command);
  if (!blankedAny) return false;
  return !(await firesFn(blanked));
}
