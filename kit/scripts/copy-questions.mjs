import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const kitRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const upstream = resolve(kitRoot, "..", "work", "bicameral-gate", "questions.mjs");
const packaged = resolve(kitRoot, "src", "questions.mjs");
const target = resolve(kitRoot, "dist", "questions.mjs");
await mkdir(dirname(target), {recursive: true});
try {
  await copyFile(upstream, packaged);
} catch {
  // Packed installs do not carry the repository work tree; use the captured package source.
}
await copyFile(packaged, target);
