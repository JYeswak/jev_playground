// run.mjs — fixture runner: cases JSONL in, verdicts NDJSON + receipt JSON out.
// --asker canned  -> answers from case.canned_p / case.canned_error ($0)
// --asker jev     -> live JevClient (needs TYPESAFE_API_KEY; budgeted runs only)
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { judge } from './gate.mjs';
import { JevClient } from './jev-client.mjs';

function parseArgs(argv) {
  const out = { cases: null, asker: 'canned', out: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--cases') out.cases = argv[++i];
    else if (argv[i] === '--asker') out.asker = argv[++i];
    else if (argv[i] === '--out') out.out = argv[++i];
  }
  if (!out.cases || !out.out) throw new Error('usage: run.mjs --cases <jsonl> --asker canned|jev --out <dir>');
  return out;
}

function expandState(c) {
  if (Array.isArray(c.state)) return c.state;
  if (typeof c.state_len === 'number') {
    return Array.from({ length: c.state_len }, (_, i) => ({ role: i % 2 ? 'assistant' : 'user', text: `filler ${i}` }));
  }
  return [];
}

function cannedAsker(c) {
  return {
    calls: 0,
    async ask() {
      this.calls += 1;
      if (c.canned_error) throw new Error('canned malformed answer');
      return { answers: { licensed: { noul: c.canned_p } } };
    },
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  let policy;
  try {
    policy = JSON.parse(readFileSync(new URL('../policy.json', import.meta.url), 'utf8'));
  } catch (err) {
    throw new Error(`cannot load policy.json: ${err?.message ?? err}`);
  }
  const lines = readFileSync(args.cases, 'utf8').split('\n').filter((l) => l.trim());
  let live = null;
  if (args.asker === 'jev') {
    live = new JevClient({ apiKey: process.env.TYPESAFE_API_KEY, model: policy.model });
  }
  const verdicts = [];
  let jevCalls = 0;
  for (const [i, line] of lines.entries()) {
    let c;
    try {
      c = JSON.parse(line);
    } catch (err) {
      console.error(`row ${i}: skipping malformed JSON (${err?.message ?? err})`);
      continue;
    }
    const a = args.asker === 'jev' ? live : cannedAsker(c);
    const v = await judge({ tool_call: c.tool_call, state: expandState(c), policy, asker: a });
    jevCalls += v.jev_called ? 1 : 0;
    verdicts.push({ id: c.id ?? `row-${i}`, expect: c.expect ?? null, ...v, asker_calls: a.calls ?? null });
  }
  mkdirSync(args.out, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15) + 'Z';
  writeFileSync(`${args.out}/verdicts-${stamp}.ndjson`, verdicts.map((v) => JSON.stringify(v)).join('\n') + '\n');
  const receipt = {
    schema: 'jev.abstention-gate-run.v1',
    asker: args.asker,
    model: args.asker === 'jev' ? policy.model : null,
    jev_calls: jevCalls,
    cases: verdicts.length,
    outcomes: Object.fromEntries([...new Set(verdicts.map((v) => v.outcome))].map((o) => [o, verdicts.filter((v) => v.outcome === o).length])),
    mismatches: verdicts.filter((v) => v.expect && v.expect !== v.outcome).map((v) => v.id),
  };
  writeFileSync(`${args.out}/receipt-${stamp}.json`, JSON.stringify(receipt, null, 1) + '\n');
  console.log(JSON.stringify(receipt));
  if (receipt.mismatches.length > 0) process.exit(3);
}

main().catch((err) => {
  console.error(`run FAILED: ${err?.message ?? err}`);
  process.exit(2);
});
