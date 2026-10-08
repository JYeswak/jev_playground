// Probe nimble's score on the backslash-rm form via the real hook path pieces.
import { RISK, STATE_CONTEXT } from "/Users/josh/Developer/jev/work/bicameral-gate/questions.mjs";

const cmd = process.argv[2] ?? "\\rm -rf /data";
const body = JSON.stringify({
  model: "nimble:latest",
  state: { command: cmd, context: STATE_CONTEXT },
  questions: RISK,
});
const res = await fetch("http://127.0.0.1:11300/omp-profile/default/v1/systemone", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body,
  signal: AbortSignal.timeout(15000),
});
console.log("http", res.status);
const data = await res.json();
const scores = {};
for (const [k, v] of Object.entries(data.answers ?? {})) scores[k] = v.noul;
console.log(JSON.stringify(scores));
