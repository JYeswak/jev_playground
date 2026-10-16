// Fixture native extension entry for installer profile-target tests.
// Extensions are registered by path (config.yml), not executed by the
// installer; the contract is loadability with a default entry export.
// Pure, no I/O, never loaded outside owned test homes.
export default function hintExtensionFixture(): { id: string } {
  return { id: "hint-fixture" };
}
