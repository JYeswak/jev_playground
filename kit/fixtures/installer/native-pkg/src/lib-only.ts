// Fixture incompatible core-only module for installer tests: a pure library
// API with named exports and NO default export. A package exposing only this
// entry must be refused before any write: it has no native hook/extension
// entry point for any declared surface.
export const LIB_ONLY = true;

export function helper(): string {
  return "helper";
}
