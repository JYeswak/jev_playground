/**
 * outcome-join — Delta 1 mechanism (structure only, no refusal wiring).
 *
 * Joins keyed decision records through `readRow` (both omp session row
 * shapes A and B — ported verbatim from work/jev-client/src/index.ts so
 * this .mjs stays dependency-free and offline). Extracts decision records
 * carrying an `outcome`/`error` field.
 *
 * Selector verification: the caller declares which fields it expects
 * (`expectKey` list). Any parsed record missing one is counted in
 * `selectorReport` — never silently dropped.
 *
 * Zero-hit guard lives here as STRUCTURE: the return carries
 * `zeroHit: true` when `matched.length === 0`. A later pass wires the
 * refusal (non-zero exit) on top of this flag.
 *
 * No Jev calls, no network, no filesystem access. Pure function.
 */

/**
 * Port of work/jev-client/src/index.ts::readRow (both shapes A/B).
 * Returns { type, data } or undefined for unparseable / foreign rows.
 */
export function readRow(line) {
  let parsed = line;
  if (typeof line === "string") {
    try {
      parsed = JSON.parse(line);
    } catch {
      return undefined;
    }
  }
  if (!parsed || typeof parsed !== "object" || !("customType" in parsed)) {
    return undefined;
  }
  const custom = parsed.customType;

  // Shape B: { customType: "…", data: {…} } — harm-rule / failure rows
  if (typeof custom === "string") {
    const data = "data" in parsed ? parsed.data : undefined;
    if (!data || typeof data !== "object") return undefined;
    return { type: custom, data: { ...data } };
  }
  // Shape A: { customType: { type: "…", data: {…} } } — observer rows
  if (custom && typeof custom === "object" && "type" in custom) {
    const type = custom.type;
    const data = "data" in custom ? custom.data : undefined;
    if (typeof type !== "string" || !data || typeof data !== "object") {
      return undefined;
    }
    return { type, data: { ...data } };
  }
  return undefined;
}

/**
 * Join decision records out of raw session rows.
 *
 * @param {object} args
 * @param {Array<unknown>} args.rows - raw lines (JSON strings or objects)
 * @param {string|string[]} [args.expectKey=[]] - fields every parsed record must carry
 * @param {string} [args.idKey="id"] - join key; decision records without it cannot join
 * @returns {{ matched: object[], unmatched: object[], selectorReport: object[],
 *            skipped: number, zeroHit: boolean }}
 *   matched: decision records with all expected fields + a usable join key.
 *   unmatched: parsed rows that cannot join ({ index, type, reason }).
 *   selectorReport: parsed rows missing ≥1 expected field ({ index, type, missing }).
 *   skipped: count of unparseable / foreign lines (never silent — counted).
 *   zeroHit: true when matched is empty (refusal wiring consumes this later).
 */
export function joinOutcomes({ rows = [], expectKey = [], idKey = "id" } = {}) {
  const expectKeys = Array.isArray(expectKey) ? expectKey : [expectKey];
  const matched = [];
  const unmatched = [];
  const selectorReport = [];
  let skipped = 0;

  const list = Array.isArray(rows) ? rows : [];
  for (let index = 0; index < list.length; index++) {
    const parsed = readRow(list[index]);
    if (!parsed) {
      skipped += 1;
      continue;
    }
    const { type, data } = parsed;

    // Selector verification first: missing an expected field → report, never drop.
    const missing = expectKeys.filter((k) => !(k in data));
    if (missing.length > 0) {
      selectorReport.push({ index, type, missing });
      continue;
    }

    // Only outcome/error-carrying records are joinable decisions.
    if (!("outcome" in data) && !("error" in data)) {
      unmatched.push({ index, type, reason: "no-outcome-or-error" });
      continue;
    }

    const id = data[idKey];
    if (id === undefined || id === null || id === "") {
      unmatched.push({ index, type, reason: `missing-id:${idKey}` });
      continue;
    }

    matched.push({ index, type, id, record: data });
  }

  return { matched, unmatched, selectorReport, skipped, zeroHit: matched.length === 0 };
}
