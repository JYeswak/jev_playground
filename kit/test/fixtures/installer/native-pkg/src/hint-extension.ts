// Fixture native extension entry for installer profile-target tests.
// Mirrors the real extension shape (see .omp/extensions/jev-claim-check.ts):
// a default factory receiving pi and registering a tool. Pure and
// deterministic, no I/O, never loaded outside owned test homes.
export type FixtureHost = {
  registerTool: (tool: unknown) => void;
};

export default function hintExtensionFixture(pi: FixtureHost): void {
  pi.registerTool({
    name: "hint-fixture-tool",
    label: "Hint fixture",
    description: "Fixture advisory tool for installer tests.",
    parameters: {},
    execute: async () => ({ allowed: true }),
  });
}
