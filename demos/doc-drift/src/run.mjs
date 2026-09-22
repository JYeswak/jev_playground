// run.mjs — corpus runner: manifest in, verdicts + gate dimensions out.
// --asker canned -> p derived from gold truth (WIRING PROOF ONLY: exercises
//   mapping, pairing, receipt. Measures nothing about judgment.)
// --asker jev    -> live Noul per pair (needs TYPESAFE_API_KEY; budgeted).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { judgePair } from './judge.mjs';
// Lane-sanctioned caller (943158c): SDK-owned wire, our failure taxonomy.
// askJevBundle passes questions through UNMODIFIED, preserving the Noul
// criteria {true,false} judgePair builds — askJev (instructions-only) would
// silently drop them.
import { askJevBundle } from '../../../work/jev-client/src/index.ts';

// Live asker via the lane client. Same refusal semantics: throw on any
// failure (transport, unconfigured, malformed) and judgePair records
// uncertain/asker-malformed. Never returns a fabricated score.
function liveAsker(apiKey, model) {
  if (!apiKey) throw new Error('TYPESAFE_API_KEY is not configured');
  return {
    async ask(state, questions) {
      const r = await askJevBundle({ state, questions, model, apiKey, timeoutMs: 20000 });
      if (!r.ok) throw new Error(`Invalid Jev answer: ${r.reason} ${r.error}`);
      return { answers: r.answers };
    },
  };
}
function parseArgs(argv) {
  const out = { corpus: null, asker: 'canned', out: null, model: 'jev-1.13.0' };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--corpus') out.corpus = argv[++i];
    else if (argv[i] === '--asker') out.asker = argv[++i];
    else if (argv[i] === '--out') out.out = argv[++i];
    else if (argv[i] === '--model') out.model = argv[++i];
  }
  if (!out.corpus || !out.out) throw new Error('usage: run.mjs --corpus <manifest> --asker canned|jev --out <dir> [--model id]');
  return out;
}

const TRUTH_P = { accurate: 0.9, drifted: 0.15, unknown: 0.55 };
const cannedAsker = (truth) => ({
  async ask() {
    return { answers: { accurate: { noul: TRUTH_P[truth] ?? 0.55 } } };
  },
});

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const man = JSON.parse(readFileSync(args.corpus, 'utf8'));
  const policy = JSON.parse(readFileSync(new URL('../policy.json', import.meta.url), 'utf8'));
  const manDir = path.dirname(path.resolve(args.corpus));
  // Manifest paths are corpus-dir-relative; fall back to manifest dir.
  const resolveFile = (p) => {
    for (const base of [path.join(manDir, 'corpus'), manDir]) {
      const full = path.join(base, p);
      try {
        readFileSync(full);
        return full;
      } catch { /* try next */ }
    }
    throw new Error(`corpus file missing: ${p}`);
  };
  let live = null;
  let jevCalls = 0;
  if (args.asker === 'jev') {
    live = liveAsker(process.env.TYPESAFE_API_KEY, args.model);
  }
  const verdicts = [];
  for (const c of man.cases) {
    const docF = c.files.find((f) => f.path.endsWith('doc.md'));
    const codeFs = c.files.filter((f) => !f.path.endsWith('doc.md'));
    const doc = docF ? readFileSync(resolveFile(docF.path), 'utf8') : null;
    const code = codeFs.length > 0
      ? codeFs.map((f) => `--- ${f.path} ---\n${readFileSync(resolveFile(f.path), 'utf8')}`).join('\n')
      : null;
    const asker = args.asker === 'jev' ? live : cannedAsker(c.truth);
    const v = await judgePair({ doc, code, anchor: c.case_id, policy, asker });
    if (args.asker === 'jev') jevCalls += v.jev_called ? 1 : 0;
    verdicts.push({ case_id: c.case_id, class: c.class, truth: c.truth, ...v });
  }
  const decided = verdicts.filter((v) => v.verdict !== 'uncertain');
  const byClass = {};
  for (const v of verdicts) {
    byClass[v.class] ??= { n: 0, match: 0 };
    byClass[v.class].n += 1;
    const want = v.truth === 'accurate' ? 'accurate' : v.truth === 'drifted' ? 'drifted' : 'uncertain';
    if (v.verdict === want) byClass[v.class].match += 1;
  }
  const drifted = verdicts.filter((v) => v.truth === 'drifted');
  const valid = verdicts.filter((v) => v.truth === 'accurate');
  const amb = verdicts.filter((v) => v.truth === 'unknown');
  const receipt = {
    schema: 'jev.docdrift.run.v1',
    asker: args.asker,
    model: args.asker === 'jev' ? args.model : null,
    jev_calls: jevCalls,
    cases: verdicts.length,
    verdicts,
    gate_dimensions: {
      drift_recall: drifted.length ? drifted.filter((v) => v.verdict === 'drifted').length / drifted.length : null,
      false_clean: drifted.length ? drifted.filter((v) => v.verdict === 'accurate').length / drifted.length : null,
      false_stale: valid.length ? valid.filter((v) => v.verdict === 'drifted').length / valid.length : null,
      attempt_rate_nonambiguous: (valid.length + drifted.length) ? decided.filter((v) => v.truth !== 'unknown').length / (valid.length + drifted.length) : null,
      withhold_on_ambiguous: amb.length ? amb.filter((v) => v.verdict === 'uncertain').length / amb.length : null,
    },
    wiring_note: args.asker === 'canned'
      ? 'CANNED asker keyed by gold truth: exercises pairing, mapping, receipt — measures NO judgment. Any accuracy number here is plumbing, not evidence.'
      : 'Live Noul per pair; see model + jev_calls.',
  };
  mkdirSync(args.out, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15) + 'Z';
  writeFileSync(`${args.out}/run-${stamp}.json`, JSON.stringify(receipt, null, 1) + '\n');
  console.log(JSON.stringify({ ...receipt, verdicts: `[${receipt.verdicts.length} omitted]` }));
}

main().catch((err) => {
  console.error(`run FAILED: ${err?.message ?? err}`);
  process.exit(2);
});
