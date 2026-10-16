// Fixture unknown-method entry for installer tests: invokes a host method
// that does not exist. The closed-world stub (like the real host) has no
// such method, so the call throws and installation refuses before writes.
export default function unknownMethodFixture(pi: unknown): void {
  // Deliberately invokes a nonexistent host method: proves the stub
  // fabricates nothing and unknown host calls fail closed like the host.
  const hostile = pi as unknown as { bogus(): void };
  hostile.bogus();
}
