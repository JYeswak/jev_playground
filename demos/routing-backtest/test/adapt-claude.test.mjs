import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import assert from 'node:assert/strict';
import test from 'node:test';

// These defend the two DECLARED RULES in bin/adapt-claude.mjs and its refusal behaviour. Both rules
// were forced into the open by failures, not designed up front: the prompt rule by the backtest's own
// NO_BASELINE_CANDIDATES floor rejecting a run where every turn qualified for the cheap model, and the
// refusal path by the requirement that a missing price is never guessed.
const BIN = new URL('../bin/adapt-claude.mjs', import.meta.url).pathname;

function work() {
  return mkdtempSync(join(tmpdir(), 'adapt-claude-'));
}

function sessionLine(model, usage) {
  return `${JSON.stringify({ type: 'assistant', message: { model, usage, content: [] } })}\n`;
}

function run(args, opts = {}) {
  return execFileSync('node', [BIN, ...args], { encoding: 'utf8', ...opts });
}

function sheet(dir, models) {
  const p = join(dir, 'prices.json');
  writeFileSync(p, JSON.stringify({
    schema: 'jev-route-backtest.claude-prices.v1',
    source: 'test fixture',
    cacheReadMultiplier: 0.1,
    cacheWriteMultiplier: 1.25,
    cacheRuleSource: 'test fixture',
    models,
  }));
  return p;
}

test('refuses to run without a price sheet rather than inventing rates', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'), sessionLine('m-1', { input_tokens: 1, output_tokens: 1 }));
  assert.throws(
    () => run([join(dir, 's.jsonl'), '--out', join(dir, 'o.jsonl')], { stdio: 'pipe' }),
    (err) => {
      assert.equal(err.status, 2);
      assert.match(String(err.stderr), /refuses to invent rates/);
      return true;
    },
  );
});

test('a model absent from the sheet is refused and NAMED, never priced', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'),
    sessionLine('known-1', { input_tokens: 10, output_tokens: 5 })
    + sessionLine('mystery-9', { input_tokens: 10, output_tokens: 5 }));
  const out = run([
    join(dir, 's.jsonl'), '--prices', sheet(dir, { 'known-1': { input: 1, output: 2 } }),
    '--out', join(dir, 'o.jsonl'),
  ]);
  const receipt = JSON.parse(out);
  assert.equal(receipt.turnsPriced, 1);
  assert.equal(receipt.turnsRefused, 1);
  assert.equal(receipt.refusedModels['mystery-9'], 1);
  assert.ok(!('known-1' in receipt.refusedModels));
});

test('context tokens are input + cacheRead + cacheWrite, per the non-author pricing ruling', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'), sessionLine('known-1', {
    input_tokens: 7, output_tokens: 3, cache_read_input_tokens: 500, cache_creation_input_tokens: 11,
  }));
  run([
    join(dir, 's.jsonl'), '--prices', sheet(dir, { 'known-1': { input: 1, output: 2 } }),
    '--out', join(dir, 'o.jsonl'),
  ]);
  const rows = readFileSync(join(dir, 'o.jsonl'), 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const msg = rows.find((r) => r.type === 'message_end');
  assert.ok(msg, 'must emit message_end; the reader ignores message_start entirely');
  // 7 + 500 + 11. Pane 2 ruled cache_creation belongs in the context fit too
  // (ruling-routing-pricing-semantics-20260918T174000Z.json): a prefix being WRITTEN to cache is
  // still occupying the context window on that turn, so a router deciding whether a cheap model
  // FITS must count it. My first rule counted only input + cacheRead and was incomplete.
  assert.equal(msg.message.usage.input, 518, 'context must include cache creation as well as reads');
  assert.equal(msg.message.usage.cacheRead, 500, 'cacheRead stays itemised for pricing');
});

test('cost is itemised and the cache multipliers are applied as declared', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'), sessionLine('known-1', {
    input_tokens: 1_000_000, output_tokens: 0, cache_read_input_tokens: 1_000_000,
    cache_creation_input_tokens: 1_000_000,
  }));
  run([
    join(dir, 's.jsonl'), '--prices', sheet(dir, { 'known-1': { input: 10, output: 20 } }),
    '--out', join(dir, 'o.jsonl'),
  ]);
  const rows = readFileSync(join(dir, 'o.jsonl'), 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const cost = rows.find((r) => r.type === 'message_end').message.usage.cost;
  assert.equal(cost.input, 10, 'one million tokens at $10/M');
  assert.equal(cost.cacheRead, 1, '0.1 x input rate, as declared');
  assert.equal(cost.cacheWrite, 12.5, '1.25 x input rate, as declared');
  assert.equal(cost.total, 23.5);
});

test('the emitted price table marks converted models recorded and the cheap candidate scenario', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'), sessionLine('known-1', { input_tokens: 5, output_tokens: 5 }));
  run([
    join(dir, 's.jsonl'),
    '--prices', sheet(dir, { 'known-1': { input: 1, output: 2 }, 'cheap-1': { input: 0.25, output: 1 } }),
    '--out', join(dir, 'o.jsonl'),
  ]);
  const table = JSON.parse(readFileSync(join(dir, 'o.jsonl.prices.json'), 'utf8'));
  assert.equal(table.models['known-1'].mode, 'recorded');
  assert.equal(table.models['cheap-1'].mode, 'scenario');
  assert.equal(table.models['cheap-1'].inputPerMillion, 0.25);
  assert.match(table.rederivation, /Claude Code records no cost/);
});

test('a sheet still carrying the template placeholders is refused, not used', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'), sessionLine('known-1', { input_tokens: 1, output_tokens: 1 }));
  const p = join(dir, 'placeholder.json');
  writeFileSync(p, JSON.stringify({
    cacheReadMultiplier: 0.1,
    cacheWriteMultiplier: 1.25,
    // Exactly what --print-price-template emits, with rates filled in and provenance left alone.
    source: 'REQUIRED: the URL or document you copied these rates from',
    cacheRuleSource: 'REQUIRED: where the cache multipliers come from; they are billing assumptions',
    models: { 'known-1': { input: 1, output: 2 } },
  }));
  assert.throws(
    () => run([join(dir, 's.jsonl'), '--prices', p, '--out', join(dir, 'o.jsonl')], { stdio: 'pipe' }),
    (err) => {
      assert.equal(err.status, 2);
      assert.match(String(err.stderr), /template placeholder/);
      return true;
    },
  );
});

// The CLI contract for the chain this adapter feeds. It lives here because this file already shells
// out to real binaries, and the flag exists only because the adapter's ruled context rule made every
// real turn exceed the hardcoded 20,000-token budget.
test('the backtest receipt records the EFFECTIVE policy, not the default', () => {
  const dir = work();
  writeFileSync(join(dir, 's.jsonl'),
    // One turn ABOVE the 50,000 budget and one below, so both floors are satisfied: the backtest
    // refuses a run with no baseline candidates AND one with no cheap candidates. My first fixture
    // put both turns under the budget and the demo correctly refused it.
    sessionLine('known-1', { input_tokens: 60_000, output_tokens: 10 })
    + sessionLine('known-1', { input_tokens: 40, output_tokens: 10 }));
  const prices = sheet(dir, { 'known-1': { input: 1, output: 2 }, 'cheap-1': { input: 0.1, output: 0.2 } });
  run([join(dir, 's.jsonl'), '--prices', prices, '--out', join(dir, 'o.jsonl')]);
  const BT = new URL('../bin/backtest.mjs', import.meta.url).pathname;
  const out = join(dir, 'bt.json');
  execFileSync('node', [
    BT, join(dir, 'o.jsonl'), '--prices', join(dir, 'o.jsonl.prices.json'),
    '--max-prompt-tokens', '50000', '--out', out,
  ], { encoding: 'utf8' });
  const receipt = JSON.parse(readFileSync(out, 'utf8'));
  // Printing DEFAULT_POLICY here would record 20000 for a run that used 50000 — a receipt that
  // misstates the assumption it ran under is worse than no receipt.
  assert.equal(receipt.policy.maxPromptTokens, 50_000);
  assert.equal(receipt.policy.maxCompletionTokens, 2_000, 'unspecified policy fields keep their defaults');
});
