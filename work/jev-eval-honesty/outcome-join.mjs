/**
 * outcome-join — Delta 1 mechanism (structure only, no refusal wiring).
 *
 * Joins keyed decision records through `readRow` (both omp session row
 * shapes A and B — ported verbatim from work/jev-client/src/index.ts so
 * this .mjs stays dependency-free and offline). Extracts decision records
 * carrying ANY of the configured `verdictKeys` (default
 * ["kind","outcome","error","verdict"] — Pass 5: live dcg-bridge decision
 * rows carry data:{kind,toolCallId[,reason]}, never outcome/error, so the
 * old outcome/error-only match joined 0/15499).
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
 * @param {string|string[]} [args.verdictKeys=["kind","outcome","error","verdict"]]
 *   - verdict field names; a record matches iff ANY listed key is present,
 *   its value carried as `verdict` on the matched entry. Unmatched only
 *   when NONE is present (reason "no-verdict-key").
 * @returns {{ matched: object[], unmatched: object[], selectorReport: object[],
 *            skipped: number, zeroHit: boolean }}
 *   matched: decision records with all expected fields + a usable join key.
 *   Each entry: { index, type, id, verdict, verdictKey, record }.
 *   unmatched: parsed rows that cannot join ({ index, type, reason }).
 *   selectorReport: parsed rows missing ≥1 expected field ({ index, type, missing }).
 *   skipped: count of unparseable / foreign lines (never silent — counted).
 *   zeroHit: true when matched is empty (refusal wiring consumes this later).
 */
export function joinOutcomes(
  { rows = [], expectKey = [], idKey = "id", verdictKeys = ["kind", "outcome", "error", "verdict"] } = {},
) {
  const expectKeys = Array.isArray(expectKey) ? expectKey : [expectKey];
  const verdictKeyList = Array.isArray(verdictKeys) ? verdictKeys : [verdictKeys];
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

    // Verdict-key match: ANY listed key present counts as the verdict field
    // carrying the outcome value (Pass 5 join-contract fix — live dcg-bridge
    // rows carry kind, not outcome/error). Unmatched only when NONE is present.
    const verdictKey = verdictKeyList.find((k) => k in data);
    if (verdictKey === undefined) {
      unmatched.push({ index, type, reason: "no-verdict-key" });
      continue;
    }

    const id = data[idKey];
    if (id === undefined || id === null || id === "") {
      unmatched.push({ index, type, reason: `missing-id:${idKey}` });
      continue;
    }

    matched.push({ index, type, id, verdict: data[verdictKey], verdictKey, record: data });
  }

  return { matched, unmatched, selectorReport, skipped, zeroHit: matched.length === 0 };
}
