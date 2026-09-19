// Same repro, with NO unhandledRejection handler: does a default Node consumer survive?
import { createServer } from "node:http";
import { TypeSafeClient } from "~/Developer/jev/upstream/typesafe-ai/typesafe-sdk-js/src/index.ts";

const server = createServer((_req, res) => {
  res.writeHead(200, { "content-type": "application/json" });
  res.flushHeaders();
});
await new Promise((r) => server.listen(0, r));
const baseURL = `http://127.0.0.1:${server.address().port}`;

const client = new TypeSafeClient({ apiKey: "k", baseURL, timeout: 200, retry: { maxRetries: 0 } });
try {
  await client.models.list();
} catch (e) {
  console.log("consumer caught:", e?.constructor?.name);
}
await new Promise((r) => setTimeout(r, 1500));
server.close();
console.log("SURVIVED: process reached the end");
process.exit(0);
