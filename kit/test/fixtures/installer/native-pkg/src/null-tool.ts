// Fixture null-tool entry for installer tests: registers a null tool.
// The call is recorded but malformed, so the advisory registration proof
// must not count it: installation refuses before writes.
export default function nullToolFixture(pi: { registerTool: (tool: unknown) => void }): void {
  pi.registerTool(null);
}
