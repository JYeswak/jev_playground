// Fixture null-handler entry for installer tests: registers the declared
// event with a non-callable handler. The registration proof must not count
// it: only callable handlers satisfy the event contract.
export default function badHandlerFixture(pi: { on: (event: string, handler: unknown) => void }): void {
  pi.on("tool_call", null);
}
