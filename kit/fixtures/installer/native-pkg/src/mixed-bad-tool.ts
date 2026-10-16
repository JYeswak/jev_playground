// Fixture mixed-registration entry for installer tests: a null tool
// registration prepended before a valid one. The host fails loading on the
// malformed call, so the whole entry must refuse even though a valid
// registration is also present.
export default function mixedBadToolFixture(pi: { registerTool: (tool: unknown) => void }): void {
  pi.registerTool(null);
  pi.registerTool({ name: "mixed-valid-tool", execute: async () => ({}) });
}
