// Fixture throwing entry for installer tests: a default function export
// that explodes when invoked. The entry loads fine, so only executing the
// factory catches it; installation must refuse before any write.
export default function throwingFixture(_pi: unknown): void {
  throw new Error("fixture-boom");
}
