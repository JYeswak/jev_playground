/**
 * The silent register — persist what every Jev call already computed.
 *
 * THE DEFECT IT CLOSES (measured, docs/demos/upstream-repro/commit-learnings-20260920.md,
 * bf12406): 21 extension packages, 18 installable, 20 tested, and exactly ONE exporting
 * any data — none of it a Jev score. 2,531 live calls were made in one night and every
 * score was discarded after the run that produced it, so the commit-judge measurement
 * had to re-score 31 commits that extensions had already seen.
 *
 * TWO DESIGN RULES, BOTH PAID FOR TONIGHT BY WATCHING jevcache FAIL:
 *
 * 1. STORE A HASH, NEVER THE INPUT. jevcache persisted the first ~200 chars of raw state
 *    in a world-readable file, with no credential rule (hyperspaceai/jevcache#1). This
 *    register stores sha256 only. There is no state_preview, and there is no option to
 *    add one. The input is unrecoverable from the register by construction.
 *
 * 2. HASH EVERY FIELD. jevcache deleted fields whose names matched a volatile-id rule
 *    BEFORE hashing, so {"command_id":"rm -rf /"} and {"command_id":"echo hello"} shared
 *    a fingerprint and it served the benign answer for the destructive command. This
 *    register canonicalises by sorting keys and drops NOTHING. Two different inputs can
 *    never collide here for that reason.
 *
 * NOT A CACHE. The register never answers a question; it only records that one was
 * answered. Replay reads it, and a replay that finds no row reports the gap rather than
 * calling the API. Caching is what made drift structurally invisible, which is why
 * jevcache was removed (8fe44b2, f717ba3).
 */
import { createHash } from 'node:crypto';
import { appendFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';

export const REGISTER_VERSION = 'jev-score-register/v1';

/** Stable across key order; drops nothing. */
export function canonicalise(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value) ?? 'null';
  if (Array.isArray(value)) return `[${value.map(canonicalise).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalise(value[k])}`).join(',')}}`;
}

/** sha256 over the canonical form. The only representation of the input we keep. */
export function inputIdentity(state) {
  return createHash('sha256').update(canonicalise(state)).digest('hex');
}

/**
 * Append one row per Jev call. Created 0600: the register holds no secrets by
 * construction, but a file nobody audited should not be world-readable either —
 * jevcache's ledger was 0644 and that was the half nobody noticed.
 */
export function recordScore(path, entry) {
  const {
    questionKey,
    score,
    model,
    state,
    identity = state === undefined ? undefined : inputIdentity(state),
    extension,
    ok = true,
    failure,
  } = entry;

  if (typeof questionKey !== 'string' || !questionKey) throw new TypeError('questionKey required');
  if (typeof identity !== 'string' || identity.length !== 64) {
    throw new TypeError('identity must be a sha256 hex digest, or pass `state` to derive one');
  }
  if (ok && typeof score !== 'number') throw new TypeError('score required unless ok:false');

  const row = {
    v: REGISTER_VERSION,
    t: new Date().toISOString(),
    extension,
    questionKey,
    score: ok ? score : null,
    model,
    identity,
    ok,
    ...(failure ? { failure } : {}),
  };

  mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
  appendFileSync(path, `${JSON.stringify(row)}\n`, { mode: 0o600 });
  return row;
}

/** Read rows back. Tolerates a torn final line — appends are not atomic across processes. */
export function readRegister(path) {
  if (!existsSync(path)) return { rows: [], malformed: 0 };
  const rows = [];
  let malformed = 0;
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    try {
      const parsed = JSON.parse(line);
      if (parsed && typeof parsed === 'object' && parsed.v === REGISTER_VERSION) rows.push(parsed);
      else malformed += 1;
    } catch {
      malformed += 1;
    }
  }
  return { rows, malformed };
}

/**
 * Wrap an ask function so every call is recorded. The wrapped function is returned
 * unchanged in behaviour — the register is a side effect, never a substitute, so a
 * recorded run and an unrecorded run produce identical answers.
 */
export function recording(ask, { path, extension, model }) {
  return async function recordedAsk(options) {
    const result = await ask(options);
    const identity = inputIdentity(options.state);
    if (result && result.ok && result.scores) {
      for (const [questionKey, score] of Object.entries(result.scores)) {
        recordScore(path, { questionKey, score: Number(score), model: result.model ?? model, identity, extension });
      }
    } else {
      recordScore(path, {
        questionKey: Object.keys(options.questions ?? { unknown: 1 })[0],
        model,
        identity,
        ok: false,
        failure: result?.failure ?? 'unknown',
        score: 0,
      });
    }
    return result;
  };
}

/**
 * The same thing for `askJevChoice`, which four extensions use (failure, firstlook,
 * fork, heat) and which returns a DIFFERENT shape: `{choice, confidence, probabilities}`,
 * with no `scores` field at all. Passing one of those through `recording()` records it
 * as a FAILURE, because `result.scores` is undefined — a silent misattribution that
 * would have written four extensions' successful calls into the register as errors.
 *
 * One row per label, keyed `<question>:<label>`, so a choice question's full
 * distribution is recoverable and not just its argmax. The chosen label gets its own
 * row keyed `<question>:__choice__` carrying the confidence as the score, so a reader
 * recovers the decision without re-deriving it from the probabilities.
 *
 * Same two rules as `recording()`: hash only, and never a cache.
 */
export function recordingChoice(ask, { path, extension, model, questionKey = 'choice' }) {
  return async function recordedChoiceAsk(options) {
    const result = await ask(options);
    const identity = inputIdentity(options.state);
    if (result && result.ok && result.probabilities) {
      for (const [label, probability] of Object.entries(result.probabilities)) {
        recordScore(path, {
          questionKey: `${questionKey}:${label}`,
          score: Number(probability),
          model: result.model ?? model,
          identity,
          extension,
        });
      }
      recordScore(path, {
        questionKey: `${questionKey}:__choice__`,
        score: Number(result.confidence),
        model: result.model ?? model,
        identity,
        extension,
      });
    } else {
      recordScore(path, {
        questionKey,
        model,
        identity,
        ok: false,
        failure: result?.failure ?? result?.reason ?? 'unknown',
        score: 0,
      });
    }
    return result;
  };
}
