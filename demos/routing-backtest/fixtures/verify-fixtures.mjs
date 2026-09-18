// verify-fixtures.mjs — proves the routing-backtest known-bad fixtures are
// actually bad, from the files on disk. No network, no key, stdlib only.
// Exit 0 = all assertions hold. Exit nonzero = the corpus is lying.
import { readFileSync, existsSync, globSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const failures = [];
const ok = (name, cond, detail = '') => {
  console.log(`${cond ? 'PASS' : 'FAIL'} ${name}${detail && !cond ? ` — ${detail}` : ''}`);
  if (!cond) failures.push(name);
};

const readLines = (f) => readFileSync(path.join(dir, f), 'utf8').split('\n').filter((l) => l.length > 0);
const rowsOf = (f) => {
  const rows = readLines(f).map((l, i) => {
    try {
      return JSON.parse(l);
    } catch {
      throw new Error(`${f}:${i + 1} is not valid JSON`);
    }
  });
  ok(`${f} parses non-empty`, rows.length > 0, 'empty file proves nothing');
  return rows;
};
const servedModels = (rows) =>
  rows
    .map((r) => r?.message)
    .filter((m) => m && typeof m === 'object' && m.role === 'assistant' && typeof m.model === 'string' && m.model.length > 0)
    .map((m) => m.model);

// 1. zero-classifiable-turns.jsonl carries ZERO served assistant models.
{
  const rows = rowsOf('zero-classifiable-turns.jsonl');
  const models = servedModels(rows);
  ok('zero-classifiable has 0 served models', models.length === 0, `found ${models.length}: ${models.join(',')}`);
}

// 2. unknown-model-turns.jsonl: manifest claims 18 model fields, all absent
// from any price table the demo ships.
{
  const rows = rowsOf('unknown-model-turns.jsonl');
  const count = rows.flatMap((r) => (r?.message && typeof r.message === 'object' && typeof r.message.model === 'string' ? [r.message.model] : [])).length;
  ok('unknown-model has exactly 18 model fields', count === 18, `found ${count}`);
  const distinct = [...new Set(rows.flatMap((r) => (r?.message && typeof r.message === 'object' && typeof r.message.model === 'string' ? [r.message.model] : [])))];
  const tables = globSync(['prices*.json', 'price-table*.json', 'src/prices*', '../prices*.json', '../src/prices*'], { cwd: dir });
  if (tables.length === 0) {
    ok('unknown-model names only the sentinel (no price table ships yet)', distinct.length === 1 && distinct[0] === 'frontier-unlisted-9x', distinct.join(','));
    console.log('NOTE no price table in tree yet — absence check becomes effective once pane 2 ships one; sentinel value asserted meanwhile');
  } else {
    const hay = tables.map((t) => readFileSync(path.join(dir, t), 'utf8')).join('\n');
    const leaked = distinct.filter((m) => hay.includes(m));
    ok(`unknown-model absent from shipped price tables (${tables.join(',')})`, leaked.length === 0, `leaked: ${leaked.join(',')}`);
  }
}

// 3. real-excerpt-t1-t6.jsonl matches manifest bytes + sha256 (recomputed).
{
  const man = JSON.parse(readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
  const entry = man.files.find((f) => f.path === 'real-excerpt-t1-t6.jsonl');
  ok('manifest names the excerpt', !!entry, 'entry missing — a manifest that cannot fail is not a manifest');
  if (entry) {
    const bytes = readFileSync(path.join(dir, entry.path));
    ok('excerpt byte count matches', bytes.length === entry.bytes, `${bytes.length} vs ${entry.bytes}`);
    ok('excerpt sha256 matches', createHash('sha256').update(bytes).digest('hex') === entry.sha256, 'hash drift = different corpus');
  }
}

if (failures.length > 0) {
  console.error(`VERIFY-FAIL ${failures.length}: ${failures.join('; ')}`);
  process.exit(1);
}
console.log('VERIFY-OK all fixture assertions hold');
