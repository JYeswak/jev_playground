export type RecordedAnswerRow = {
  id: string;
  answers: Record<string, unknown>;
  model?: string;
  usage?: Record<string, unknown>;
};

type FakeResponse = {
  ok: true;
  status: 200;
  headers: { get(name: string): string | null };
  body: null;
  clone(): FakeResponse;
  text(): Promise<string>;
};

function responseFor(row: RecordedAnswerRow): FakeResponse {
  const payload = JSON.stringify({
    answers: row.answers,
    ...(row.model ? { model: row.model } : {}),
    ...(row.usage ? { usage: row.usage } : {}),
  });
  const response: FakeResponse = {
    ok: true,
    status: 200,
    headers: { get: (name: string) => (name.toLowerCase() === "content-type" ? "application/json" : null) },
    body: null,
    clone: () => response,
    text: async () => payload,
  };
  return response;
}

export function createFakeFetch(rows: readonly RecordedAnswerRow[]): typeof fetch {
  let index = 0;
  return (async () => {
    if (index >= rows.length) throw new Error("fake asker exhausted recorded rows");
    const row = rows[index++];
    return responseFor(row) as unknown as Response;
  }) as typeof fetch;
}

export class RecordedFakeAsker {
  readonly fetch: typeof fetch;

  constructor(rows: readonly RecordedAnswerRow[]) {
    this.fetch = createFakeFetch(rows);
  }
}
