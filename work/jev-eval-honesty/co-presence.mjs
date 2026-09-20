/**
 * co-presence — Delta 2 mechanism with the zero-hit refusal WIRED (Wave B §6 P3).
 *
 * Consumes the `zeroHit` structure from outcome-join.mjs (`joinOutcomes`).
 * Before any absence claim is reported, proves the subject join key against
 * a known-firing neighbour row set passed in by the caller (same
 * session/profile scope — the caller scopes the rows, this module never
 * fetches).
 *
 * Verdicts:
 *   REFUSE               — joinResult.zeroHit is true. The selector matched
 *                          nothing, so reporting "absent" would launder an
 *                          empty join into a finding. Refuse instead.
 *   PRESENT              — subject key found in joinResult.matched.
 *   ABSENT-NEXT-TO-FIRING— subject key missing while ≥1 neighbour row fired
 *                          in scope. Means NOT-LOADED (missing pi.on / glob
 *                          miss / not on extensions list) — never "no traffic".
 *   ABSENT-NO-NEIGHBOUR  — subject key missing and no neighbour rows fired
 *                          in scope. No co-presence evidence either way.
 *
 * No Jev calls, no network, no filesystem access. Pure function.
 */

/** Exact refusal string — asserted verbatim by co-presence.test.mjs. */
export const ZERO_HIT_REASON =
  "zero-hit: selector matched nothing; refusing to report absence as finding";

/**
 * Extract the join-key value from a matched decision record (or neighbour row).
 * Tolerates flat records (`{ id }`) and wrapped rows (`{ data: { id } }`).
 */
function keyOf(record, idKey) {
  if (!record || typeof record !== "object") return undefined;
  if (record[idKey] !== undefined) return record[idKey];
  const data = record.data;
  if (data && typeof data === "object" && data[idKey] !== undefined) return data[idKey];
  // joinOutcomes matched entries carry the join key as top-level `id`
  // (shape {index, type, id, verdict, verdictKey, record}) — neither
  // record[idKey] nor record.data[idKey] exists on them, so without this
  // fallback a subject row inside the neighbour set reads ABSENT-NEXT-TO-FIRING.
  if (record.id !== undefined) return record.id;
  return undefined;
}

/**
 * Check subject co-presence against a known-firing neighbour row set.
 *
 * @param {object} args
 * @param {object} args.joinResult - `joinOutcomes` return
 *   (`{ matched, zeroHit }`; only those two fields are read).
 * @param {object|Array} args.neighbour - known-firing neighbour row set in
 *   the same session/profile scope. Object form:
 *   `{ key, rows, idKey?, scope? }` where `key` is the subject join key,
 *   `rows` the neighbour rows, `idKey` the join-key field (default `"id"`),
 *   `scope` a label for the detail string. A bare array is treated as `rows`
 *   with no subject key.
 * @returns {{ verdict: string, reason?: string, detail?: string }}
 */
export function checkPresence({ joinResult, neighbour } = {}) {
  // The refusal, wired — not structure: an empty join is never reportable
  // as an absence finding, no matter what the neighbour set looks like.
  if (joinResult?.zeroHit === true) {
    return { verdict: "REFUSE", reason: ZERO_HIT_REASON };
  }

  const asObject = Array.isArray(neighbour) ? { rows: neighbour } : (neighbour ?? {});
  const idKey = asObject.idKey ?? "id";
  const key = asObject.key ?? asObject.id;
  const rows = Array.isArray(asObject.rows) ? asObject.rows : [];
  const scope = asObject.scope ?? "same session/profile scope";

  const matched = Array.isArray(joinResult?.matched) ? joinResult.matched : [];
  const hits = key === undefined ? 0 : matched.filter((m) => keyOf(m, idKey) === key).length;

  if (hits > 0) {
    return {
      verdict: "PRESENT",
      detail:
        `key '${key}' present in ${hits} matched record(s); ` +
        `${rows.length} neighbour row(s) in scope '${scope}'.`,
    };
  }

  const subject = key === undefined ? "(unspecified key)" : `key '${key}'`;
  if (rows.length > 0) {
    return {
      verdict: "ABSENT-NEXT-TO-FIRING",
      detail:
        `${subject} absent while ${rows.length} neighbour row(s) fired ` +
        `in scope '${scope}' — not-loaded (missing pi.on / glob miss / ` +
        `not on extensions list), never 'no traffic'.`,
    };
  }
  return {
    verdict: "ABSENT-NO-NEIGHBOUR",
    detail:
      `${subject} absent and no neighbour rows fired in scope '${scope}' — ` +
      `no co-presence evidence; cannot distinguish not-loaded from no-traffic.`,
  };
}
