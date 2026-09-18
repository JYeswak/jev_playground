#!/usr/bin/env node
// adapt-claude — convert Claude Code session JSONL into the transcript shape this demo reads.
//
// WHY THIS EXISTS. `--mine` pointed the backtest at 4,626 real Claude Code sessions and it returned
// EMPTY_CLASSIFIABLE_SET: no classifiable turns at all. The reader needs `message.usage.cost.total`
// and a recorded served model; Claude Code records `message.usage.input_tokens`,
// `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens` and a model string, with
// NO cost field anywhere. So the demo's headline was proof the accounting works, not that it works on
// anyone's data — recorded as NEGATIVE_EVIDENCE R20, a refuted hypothesis rather than a limitation,
// because the README implied the fixture shape generalizes and --mine falsified that.
//
// Pane 3 ruled FIX over "state the limit" and over "retire the headline"
// (docs/demos/duel-2/runs/routing-scope-ruling-20260918T174327Z.json, c7da940), with constraints:
// exact model strings, mechanical renames only, prices from a published sheet, ONE declared cache
// rule, and the refusal preserved for anything unknowable. This honours all five.
//
// IT IS A SEPARATE FILE ON PURPOSE. Editing src/transcript-reader.mjs would have put 21 tests and a
// seven-mutation harness at risk to serve one input shape. Conversion is a seam, so the demo stays
// exactly as verified and this file carries the new assumptions where a reader can see them.
//
// WHAT IS MECHANICAL, AND THEREFORE SAFE:
//   input_tokens                  -> usage.input
//   output_tokens                 -> usage.output
//   cache_read_input_tokens       -> usage.cacheRead
//   cache_creation_input_tokens   -> usage.cacheWrite
//   message.model                 -> message.model, VERBATIM. Never normalised, never guessed.
//
// WHAT IS NOT MECHANICAL, AND THEREFORE REFUSED RATHER THAN INVENTED: the money. Claude Code records
// no cost, so a dollar figure can only come from a price sheet. This tool does not ship one and does
// not embed rates. You pass `--prices <file>`; a model absent from that file makes its turns
// unclassifiable with the model named, exactly as the demo already refuses unpriced models. A
// classifier that guesses a price is worse than one that refuses, and refusing is what it does today.
//
// THE ONE DECLARED CACHE RULE, stated here and copied into every receipt this produces:
//   cache reads bill at cacheReadMultiplier x the model's input rate
//   cache writes bill at cacheWriteMultiplier x the model's input rate
// Both multipliers come from the price file. They are ASSUMPTIONS about your provider's billing, not
// measurements, and the receipt says so in its own rederivation string.
//
// Usage:
//   adapt-claude.mjs <dir-or-file>... --prices <file> --out <converted.jsonl>
//   adapt-claude.mjs --print-price-template
import fs from 'node:fs';
import path from 'node:path';

const TEMPLATE = {
  schema: 'jev-route-backtest.claude-prices.v1',
  as_of: 'YYYY-MM-DD — the date you read the provider price sheet',
  currency: 'USD',
  unit: 'USD per million tokens',
  source: 'REQUIRED: the URL or document you copied these rates from',
  cacheReadMultiplier: 0.1,
  cacheWriteMultiplier: 1.25,
  cacheRuleSource: 'REQUIRED: where the cache multipliers come from; they are billing assumptions',
  models: {
    'claude-opus-5': { input: null, output: null },
    'claude-sonnet-5': { input: null, output: null },
  },
};

function die(msg, code = 2) {
  console.error(`adapt-claude: ${msg}`);
  process.exit(code);
}

function parseArgs(argv) {
  const inputs = [];
  let prices = null;
  let out = null;
  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === '--print-price-template') return { template: true };
    else if (a === '--prices') prices = argv[++i] ?? die('--prices needs a path');
    else if (a === '--out') out = argv[++i] ?? die('--out needs a path');
    else if (a.startsWith('--')) die(`unknown option: ${a}`);
    else inputs.push(a);
  }
  if (!inputs.length) die('at least one directory or .jsonl file is required');
  if (!prices) die('--prices <file> is required. This tool refuses to invent rates; run --print-price-template');
  if (!out) die('--out is required so the conversion is receipted');
  return { inputs, prices, out };
}

function collect(target, acc) {
  const st = fs.statSync(target);
  if (st.isDirectory()) {
    for (const entry of fs.readdirSync(target)) collect(path.join(target, entry), acc);
  } else if (target.endsWith('.jsonl')) acc.push(target);
  return acc;
}

function main() {
  const args = parseArgs(process.argv);
  if (args.template) {
    console.log(JSON.stringify(TEMPLATE, null, 2));
    return 0;
  }
  let sheet;
  try {
    sheet = JSON.parse(fs.readFileSync(args.prices, 'utf8'));
  } catch (err) {
    die(`price file unreadable: ${err.message}`);
  }
  for (const field of ['cacheReadMultiplier', 'cacheWriteMultiplier', 'models']) {
    if (sheet[field] === undefined) die(`price file has no ${field}`);
  }
  const readMult = Number(sheet.cacheReadMultiplier);
  const writeMult = Number(sheet.cacheWriteMultiplier);
  if (!Number.isFinite(readMult) || !Number.isFinite(writeMult)) die('cache multipliers must be numbers');

  const files = args.inputs.flatMap((t) => collect(t, []));
  if (!files.length) die('no .jsonl files found under the supplied paths');

  const lines = [];
  const skippedModels = new Map();
  const pricedModels = new Set();
  const cacheRuleText = `cacheRead = ${readMult} x input rate; cacheWrite = ${writeMult} x input rate`;
  let turns = 0;
  let priced = 0;

  lines.push(JSON.stringify({
    type: 'session',
    version: 'adapt-claude.v1',
    id: 'adapted',
    timestamp: new Date().toISOString(),
    cwd: process.cwd(),
    // The assumptions travel WITH the data, so a receipt derived from this can never be read as
    // though the money were recorded rather than computed.
    adapted_from: 'claude-code-session-jsonl',
    price_source: sheet.source ?? 'UNSTATED — the price file did not name its source',
    cache_rule: `cacheRead = ${readMult} x input rate; cacheWrite = ${writeMult} x input rate`,
    cache_rule_source: sheet.cacheRuleSource ?? 'UNSTATED — the price file did not name its cache source',
  }));

  for (const file of files) {
    let raw;
    try {
      raw = fs.readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    for (const line of raw.split('\n')) {
      if (!line.trim()) continue;
      let row;
      try {
        row = JSON.parse(line);
      } catch {
        continue;
      }
      const msg = row?.message;
      const u = msg?.usage;
      if (row?.type !== 'assistant' || !u || !msg?.model) continue;
      turns += 1;
      const model = String(msg.model);
      const rate = sheet.models?.[model];
      const input = Number(u.input_tokens) || 0;
      const output = Number(u.output_tokens) || 0;
      const cacheRead = Number(u.cache_read_input_tokens) || 0;
      const cacheWrite = Number(u.cache_creation_input_tokens) || 0;

      if (!rate || !Number.isFinite(Number(rate.input)) || !Number.isFinite(Number(rate.output))) {
        // REFUSED, not guessed, and the model is named so the reader can add it to the sheet.
        skippedModels.set(model, (skippedModels.get(model) ?? 0) + 1);
        continue;
      }
      const inRate = Number(rate.input) / 1e6;
      const outRate = Number(rate.output) / 1e6;
      const cost = {
        input: input * inRate,
        output: output * outRate,
        cacheRead: cacheRead * inRate * readMult,
        cacheWrite: cacheWrite * inRate * writeMult,
      };
      cost.total = cost.input + cost.output + cost.cacheRead + cost.cacheWrite;
      priced += 1;
      pricedModels.add(model);

      lines.push(JSON.stringify({ type: 'turn_start' }));
      lines.push(JSON.stringify({
        // message_end, NOT message_start: the reader consumes only `message` and `message_end` rows
        // and silently ignores `message_start`. My first version emitted message_start, converted 500
        // real turns, and still got EMPTY_CLASSIFIABLE_SET — a conversion that produced perfectly
        // shaped rows the reader never looks at. Found by reading its grouping loop, not by guessing.
        type: 'message_end',
        message: {
          role: 'assistant',
          model,
          content: (msg.content ?? []).map((part) => (
            part?.type === 'tool_use' ? { type: 'toolCall', name: part.name } : { type: 'text', text: '' }
          )),
          usage: {
            // THE SECOND DECLARED RULE, and the demo's own floor forced it into the open. Emitting
            // usage.input as the raw input_tokens made EVERY turn qualify for the cheap model, and
            // the backtest refused the run with NO_BASELINE_CANDIDATES: "every turn qualifies for the
            // cheap scenario". It was right to refuse. A Claude turn with input_tokens=2 and
            // cache_read_input_tokens=55141 is not a 2-token prompt — the model processes the whole
            // cached prefix, so the PROMPT the router would have to fit is input + cacheRead. The
            // cost fields below stay itemised, so the cached share is still priced at its own rate.
            input: input + cacheRead,
            output,
            cacheRead,
            cacheWrite,
            promptRule: 'prompt = input_tokens + cache_read_input_tokens (declared; the cached prefix is processed)',
            totalTokens: input + output + cacheRead + cacheWrite,
            cost,
          },
        },
      }));
    }
  }

  fs.writeFileSync(args.out, `${lines.join('\n')}\n`);

  // ALSO EMIT THE DEMO'S OWN PRICE-TABLE SHAPE, rather than inventing a second format for the same
  // facts. src/pricing.mjs expects models keyed by mode: "recorded" means the cost is in the log,
  // "scenario" means it is computed from inputPerMillion/outputPerMillion. Every model we priced here
  // becomes "recorded", because this conversion WROTE those costs into the transcript; the cheap
  // candidate stays "scenario", because it never ran and its rates are an assumption by construction.
  // Two formats for one truth is the drift class this repo gates against in its own documents.
  const pricedList = [...pricedModels];
  const table = {
    schema: 'jev-route-backtest.price-table.v1',
    as_of: sheet.as_of ?? 'UNSTATED',
    currency: sheet.currency ?? 'USD',
    unit: 'USD per million tokens for scenario prices',
    rederivation:
      'Baseline spend was COMPUTED by bin/adapt-claude.mjs from the supplied sheet and the declared '
      + 'cache rule, because Claude Code records no cost field. It is therefore "recorded" only in '
      + 'the sense that the converted transcript now carries it. '
      + `Price source: ${sheet.source ?? 'UNSTATED'}. Cache rule: ${cacheRuleText}.`,
    models: Object.fromEntries([
      ...pricedList.map((m) => [m, { source: `computed by adapt-claude from ${args.prices}`, mode: 'recorded' }]),
      ['cheap-1', {
        source: sheet.cheap?.source ?? 'scenario assumption; refresh before live use',
        mode: 'scenario',
        inputPerMillion: Number(sheet.models?.['cheap-1']?.input ?? 0.2),
        outputPerMillion: Number(sheet.models?.['cheap-1']?.output ?? 0.8),
      }],
    ]),
  };
  const tablePath = `${args.out}.prices.json`;
  fs.writeFileSync(tablePath, `${JSON.stringify(table, null, 2)}\n`);
  const receipt = {
    schema: 'jev-route-backtest.claude-adapt.v1',
    generated_at: new Date().toISOString(),
    files: files.length,
    assistantTurnsSeen: turns,
    turnsPriced: priced,
    turnsRefused: turns - priced,
    refusedModels: Object.fromEntries(skippedModels),
    cacheRule: `cacheRead = ${readMult} x input; cacheWrite = ${writeMult} x input`,
    rederivation:
      'Claude Code records NO cost field. Every dollar figure downstream of this conversion is '
      + 'COMPUTED from the supplied price sheet and the declared cache multipliers, which are '
      + 'assumptions about provider billing rather than measurements. Turns whose model is absent '
      + 'from the sheet are refused and counted, never priced by guess.',
    output: args.out,
    priceTableOut: `${args.out}.prices.json`,
  };
  console.log(JSON.stringify(receipt));
  return priced > 0 ? 0 : 3;
}

process.exit(main());
