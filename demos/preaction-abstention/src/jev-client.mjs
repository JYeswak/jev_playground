// Minimal Jev client: one Noul question, pinned model, no silent fallback.
export class JevClient {
  constructor({ apiKey, model, fetchFn = globalThis.fetch }) {
    if (!apiKey) throw new Error('TYPESAFE_API_KEY is not configured');
    this.apiKey = apiKey;
    this.model = model;
    this.fetchFn = fetchFn;
  }
  url() {
    return 'https://api.typesafe.ai/v1/systemone';
  }

  // asker.ask(state, questions) -> { answers: { <name>: { noul: number } } }
  async ask(state, questions) {
    const res = await this.fetchFn(this.url(), {
      method: 'POST',
      headers: { Authorization: `Bearer ${this.apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: this.model, state, questions }),
    });
    const text = await res.text();
    let body;
    try {
      body = JSON.parse(text);
    } catch {
      throw new Error(`Invalid Jev answer: non-JSON (status ${res.status})`);
    }
    if (!res.ok || !body || typeof body.answers !== 'object') {
      throw new Error(`Invalid Jev answer: status ${res.status}`);
    }
    return body;
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
