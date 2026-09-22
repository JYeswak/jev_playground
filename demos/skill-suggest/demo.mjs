#!/usr/bin/env node
// Riff on the official skill-suggestion cookbook. Keyless by default: a tiny
// fixture roster stands in for the 182-skill Hermes catalog, and recorded
// overlap scores stand in for the two TypeSafe calls (rank-all, then verify
// the top three with a gate). Fixture suggestions are not a live ranking.
// `node demos/skill-suggest/demo.mjs --live` runs the cookbook's two requests
// per task through work/jev-client, model jev-1.13.0: rank-all Choice, then a
// Choice over the top three plus one fits Noul per candidate; the winner is
// suggested only when its fits noul reaches the cookbook's 0.30, else nothing.
// NO-CLAIM: nothing here calls Jev; see INJECTION-FLAG-RESULT.md for a measured seat.
import { suggest, ROSTER } from "./suggest.mjs";

const TASKS = [
  "Cut many iPhone takes of a lip-synced performance into a music video locked to a clean master track.",
  "Black-box sensitive content in a macOS screen recording before upload.",
  "Post this to Mastodon.",
];

const live = process.argv.includes("--live");
let askLive = null;
if (live) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  askLive = async (text) => {
    const rank = await askJevBundle({
      model: "jev-1.13.0",
      state: { task: text },
      questions: {
        which: {
          type: "choice",
          instructions: "Which skill fits the task best?",
          criteria: Object.fromEntries(ROSTER.map((s) => [s.name, s.description])),
        },
      },
      timeoutMs: 20000,
    });
    if (!rank.ok) {
      console.error(`live call failed: ${rank.reason} ${rank.error}`);
      process.exit(2);
    }
    const probs = rank.answers.which.probabilities;
    const top3 = Object.keys(probs).sort((a, b) => probs[b] - probs[a]).slice(0, 3);
    const full = Object.fromEntries(ROSTER.map((s) => [s.name, s]));
    const questions = {
      which: {
        type: "choice",
        instructions: "Which of these skills does the task need?",
        criteria: Object.fromEntries(top3.map((n) => [n, `${full[n].description}. ${full[n].detail}`])),
      },
    };
    for (const n of top3) {
      questions[`fits::${n}`] = {
        type: "noul",
        instructions: `Does the skill '${n}' do the specific thing the task asks for? It is described as: ${full[n].description}. ${full[n].detail}`,
      };
    }
    const verify = await askJevBundle({ model: "jev-1.13.0", state: { task: text }, questions, timeoutMs: 20000 });
    if (!verify.ok) {
      console.error(`live call failed: ${verify.reason} ${verify.error}`);
      process.exit(2);
    }
    const winner = verify.answers.which.choice;
    const fits = verify.answers[`fits::${winner}`].noul;
    if (!(fits >= 0.30)) return { skill: null, best: fits };
    return { skill: winner, score: fits };
  };
}
let failed = 0;
for (const text of TASKS) {
  const r = live ? await askLive(text) : suggest(text, ROSTER);
  if (r.skill) console.log(`suggest: ${r.skill}  (score=${r.score.toFixed(2)})  <-  ${text.slice(0, 60)}…`);
  else console.log(`suggest: nothing (best=${r.best.toFixed(2)} below gate)  <-  ${text.slice(0, 60)}…`);
}
if (TASKS.length !== 3) { console.error("fixture changed shape"); failed = 1; }


process.exit(failed);
