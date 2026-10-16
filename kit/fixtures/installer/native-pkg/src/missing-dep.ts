// Fixture missing-dependency entry for installer tests: a well-formed
// default factory whose relative import does not exist. Loading must fail
// closed (module not found), never install.
import { doesNotExist } from "./nonexistent-relative.js";

export default function missingDepFixture(pi: { on: (event: string, handler: (event: unknown) => Promise<unknown>) => void }): void {
  void doesNotExist;
  pi.on("tool_call", async () => ({ block: false, reason: "missing-dep" }));
}
