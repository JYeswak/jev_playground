// Fixture inert hook entry for installer tests: a default function export
// that never registers any host event. The installer must refuse it for
// hook mechanisms (no registration proof), even though it loads cleanly.
export default function inertHookFixture(_pi: unknown): void {
}
