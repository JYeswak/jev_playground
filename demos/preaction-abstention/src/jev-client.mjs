// Lane-sanctioned Jev client: one Noul question, pinned model, no silent fallback.
// Wire owned by work/jev-client (943158c): SDK-owned transport, our failure taxonomy.
// askJevBundle passes questions through UNMODIFIED, preserving the Noul
// criteria {true,false} gate.mjs builds — askJev (instructions-only) would
// silently drop them.
import { askJevBundle } from '../../../work/jev-client/src/index.ts';

export class JevClient {
  constructor({ apiKey, model }) {
    if (!apiKey) throw new Error('TYPESAFE_API_KEY is not configured');
    this.apiKey = apiKey;
    this.model = model;
  }

  // asker.ask(state, questions) -> { answers: { <name>: { noul: number } } }
  // Throws on any failure (transport, unconfigured, malformed); gate.mjs
  // turns a throw into withhold, never a fabricated pass.
  async ask(state, questions) {
    const r = await askJevBundle({ state, questions, model: this.model, apiKey: this.apiKey, timeoutMs: 20000 });
    if (!r.ok) throw new Error(`Invalid Jev answer: ${r.reason} ${r.error}`);
    return { answers: r.answers };
  }

  // Extract one Noul probability, refusing (never coercing) anything else.
  static noul(response, name) {
    const a = response?.answers?.[name];
    if (!a || !('noul' in a) || typeof a.noul !== 'number' || !Number.isFinite(a.noul)) {
      throw new Error(`Invalid Jev answer for ${name}`);
    }
    return a.noul;
  }
}
