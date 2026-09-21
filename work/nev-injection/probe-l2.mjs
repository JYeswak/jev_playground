/**
 * L2 probe: does get_state.systemPrompt list xd://jev_flag_ext_probe?
 * Arms: default (expect PRESENT), --no-extensions (expect ABSENT),
 * nonce xd://zzzz_no_such_tool_9c42 (expect ABSENT — guards against a
 * matcher that reports everything present).
 * Keyless, offline, zero model calls. Writes annot-l2-result.json.
 * Exit 0 all arms as expected, 1 otherwise.
 */
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROBE = "xd://jev_flag_ext_probe";
const NONCE = "xd://zzzz_no_such_tool_9c42";

function query(extraArgs) {
  const input = [
    JSON.stringify({ id: "p1", type: "negotiate_protocol", protocolVersion: 2 }),
    JSON.stringify({ id: "s1", type: "get_state" }),
  ].join("\n") + "\n";
  const r = spawnSync("omp", ["--mode=rpc", "--max-time=25", ...extraArgs],
    { input, encoding: "utf8", timeout: 60000, cwd: "/Users/josh/Developer/jev" });
  return (r.stdout || "") + (r.stderr || "");
}

const full = query([]);
const noext = query(["--no-extensions"]);
const result = {
  date: new Date().toISOString().slice(0, 10),
  profile: process.env.OMP_PROFILE || process.env.PI_PROFILE || "unknown",
  arms: {
    default_present: full.includes(PROBE),
    noext_absent: !noext.includes(PROBE),
    nonce_absent: !full.includes(NONCE),
  },
  full_bytes: full.length,
  noext_bytes: noext.length,
};
result.pass = result.arms.default_present && result.arms.noext_absent && result.arms.nonce_absent;
writeFileSync(join(HERE, "annot-l2-result.json"), JSON.stringify(result, null, 2) + "\n");
console.log(JSON.stringify(result.arms));
console.log(result.pass ? "L2-PROBE PASS" : "L2-PROBE FAIL");
process.exit(result.pass ? 0 : 1);
