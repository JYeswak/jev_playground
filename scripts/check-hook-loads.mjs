import { existsSync, lstatSync, readFileSync, readdirSync, realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { createHash } from "node:crypto";

const sourceExtensions = new Set([".cjs", ".js", ".jsx", ".mjs", ".mts", ".cts", ".ts", ".tsx"]);
const problems = [];
const entrypoints = new Map();
const extensionEntries = new Map();
const visitedDirectories = new Set();

function argument(name, fallback) {
  const index = Bun.argv.indexOf(name);
  return index < 0 ? fallback : Bun.argv[index + 1];
}

const repo = resolve(argument("--repo", process.cwd()));
const home = resolve(argument("--home", Bun.env.HOME || ""));

function display(file) {
  const absolute = resolve(file);
  const repoRelative = relative(repo, absolute);
  if (repoRelative !== ".." && !repoRelative.startsWith(`..${sep}`) && !isAbsolute(repoRelative)) {
    return repoRelative || ".";
  }
  const homeRelative = relative(home, absolute);
  if (homeRelative !== ".." && !homeRelative.startsWith(`..${sep}`) && !isAbsolute(homeRelative)) {
    return `~/${homeRelative}`;
  }
  return `external:${createHash("sha256").update(absolute).digest("hex").slice(0, 12)}`;
}

function problem(file, message) {
  problems.push(`${display(file)}: ${message}`);
}

function addEntrypoint(file) {
  try {
    const real = realpathSync(file);
    if (sourceExtensions.has(extname(real))) entrypoints.set(real, display(real));
  } catch {
    problem(file, "installed source is unreadable");
  }
}

function extname(file) {
  const name = file.slice(file.lastIndexOf(sep) + 1);
  const dot = name.lastIndexOf(".");
  return dot < 0 ? "" : name.slice(dot);
}

function walk(directory) {
  let real;
  try {
    real = realpathSync(directory);
    if (visitedDirectories.has(real)) return;
    visitedDirectories.add(real);
    for (const item of readdirSync(real, { withFileTypes: true })) {
      const child = join(real, item.name);
      if (item.isDirectory()) walk(child);
      else if (item.isFile()) addEntrypoint(child);
      else if (item.isSymbolicLink()) {
        try {
          const stat = lstatSync(child);
          if (stat.isSymbolicLink()) {
            const target = realpathSync(child);
            if (sourceExtensions.has(extname(target))) addEntrypoint(target);
            else walk(target);
          }
        } catch {
          problem(child, "installed symlink target is unreadable");
        }
      }
    }
  } catch {
    problem(directory, "installed directory is unreadable");
  }
}

function sourceDirectory(directory) {
  if (!existsSync(directory)) return;
  walk(directory);
}

function stripComment(line) {
  let quote = "";
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (quote) {
      if (character === quote && line[index - 1] !== "\\") quote = "";
    } else if (character === "'" || character === '"') {
      quote = character;
    } else if (character === "#") {
      return line.slice(0, index);
    }
  }
  return line;
}

function scalar(value) {
  const trimmed = value.trim();
  if (trimmed.length >= 2 &&
      ((trimmed[0] === '"' && trimmed.at(-1) === '"') ||
       (trimmed[0] === "'" && trimmed.at(-1) === "'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function extensionsFromConfig(file) {
  let text;
  try {
    text = readFileSync(file, "utf8");
  } catch {
    problem(file, "listed config is unreadable");
    return;
  }
  const lines = text.split("\n");
  for (let index = 0; index < lines.length; index += 1) {
    const clean = stripComment(lines[index].replaceAll("\r", ""));
    const trimmed = clean.trim();
    if (!trimmed.startsWith("extensions:")) continue;
    const indent = clean.length - clean.trimStart().length;
    const tail = trimmed.slice("extensions:".length).trim();
    if (tail === "[]") continue;
    if (tail !== "") {
      const values = tail.startsWith("[") && tail.endsWith("]")
        ? tail.slice(1, -1).split(",").map(scalar)
        : [scalar(tail)];
      for (const value of values) if (value) addExtensionEntry(file, value);
      continue;
    }
    for (index += 1; index < lines.length; index += 1) {
      const next = stripComment(lines[index].replaceAll("\r", ""));
      const nextTrimmed = next.trim();
      if (!nextTrimmed) continue;
      const nextIndent = next.length - next.trimStart().length;
      if (nextIndent <= indent) {
        index -= 1;
        break;
      }
      if (!nextTrimmed.startsWith("-")) {
        problem(file, "unsupported extension-list entry");
        continue;
      }
      const value = scalar(nextTrimmed.slice(1));
      if (value) addExtensionEntry(file, value);
    }
  }
}

function resolveExtension(config, value) {
  let expanded = value;
  if (expanded.startsWith("~/")) expanded = join(home, expanded.slice(2));
  if (isAbsolute(expanded)) return resolve(expanded);
  const configDirectory = dirname(config);
  const candidates = [resolve(repo, expanded), resolve(configDirectory, expanded), resolve(home, expanded)];
  return candidates.find((candidate) => existsSync(candidate)) || candidates[0];
}

function addExtensionEntry(config, value) {
  const target = resolveExtension(config, value);
  extensionEntries.set(target, config);
  try {
    const stat = statSync(target);
    if (stat.isDirectory()) walk(target);
    else addEntrypoint(target);
  } catch {
    problem(config, `listed extension is missing: ${display(target)}`);
  }
}


function readExpected() {
  const file = join(repo, "work", "jev-inventory", "expected.json");
  try {
    return JSON.parse(readFileSync(file, "utf8"));
  } catch {
    problem(file, "expected-surface inventory is unreadable");
    return { profiles: [], surfaces: [] };
  }
}

function configuredExtensions(expected) {
  const configs = [join(repo, ".omp", "config.yml"), join(home, ".omp", "agent", "config.yml")];
  for (const profile of expected.profiles || []) {
    if (profile !== "default") {
      configs.push(join(home, ".omp", "profiles", profile, "agent", "config.yml"));
    }
  }
  for (const config of configs) {
    if (existsSync(config)) extensionsFromConfig(config);
    else problem(config, "claimed profile config is missing");
  }
}

function checkExpected(expected) {
  for (const surface of expected.surfaces || []) {
    if (surface.expect !== "on") continue;
    if (surface.group === "hook" && surface.file) {
      const file = resolve(repo, surface.file);
      if (!existsSync(file)) problem(file, `expected-on hook is missing: ${surface.id}`);
      else addEntrypoint(file);
    } else if (surface.group === "extension" && surface.extension) {
      const target = resolveExtension(join(repo, ".omp", "config.yml"), surface.extension);
      if (!extensionEntries.has(target)) problem(target, `expected-on extension is not listed: ${surface.id}`);
    } else if (surface.group === "global" && surface.hookfile) {
      for (const profile of expected.profiles || []) {
        const agent = profile === "default"
          ? join(home, ".omp", "agent")
          : join(home, ".omp", "profiles", profile, "agent");
        const file = join(agent, "hooks", "post", surface.hookfile);
        if (!existsSync(file)) problem(file, `expected-on global hook is missing: ${surface.id}`);
        else addEntrypoint(file);
      }
    }
  }
}

const expected = readExpected();
for (const directory of [
  join(repo, ".omp", "hooks", "pre"),
  join(repo, ".omp", "hooks", "post"),
  join(repo, ".omp", "extensions"),
  join(home, ".omp", "omp-extensions"),
  join(home, ".omp", "agent", "hooks", "pre"),
  join(home, ".omp", "agent", "hooks", "post"),
]) sourceDirectory(directory);

for (const profile of expected.profiles || []) {
  if (profile === "default") continue;
  const agent = join(home, ".omp", "profiles", profile, "agent");
  sourceDirectory(join(agent, "hooks", "pre"));
  sourceDirectory(join(agent, "hooks", "post"));
}

configuredExtensions(expected);
checkExpected(expected);

if (entrypoints.size > 0) {
  try {
    const result = await Bun.build({
      entrypoints: [...entrypoints.keys()],
      target: "bun",
      packages: "external",
      write: false,
      logLevel: "silent",
    });
    for (const log of result.logs) {
      if (log.level === "error") {
        const source = log.position?.file || "<installed entrypoint>";
        const location = log.position ? `:${log.position.line}:${log.position.column}` : "";
        problem(source, `parse/import failure${location}`);
      }
    }
  } catch (error) {
    const messages = error instanceof AggregateError ? error.errors : [];
    for (const message of messages) {
      const source = message.position?.file || "<installed entrypoint>";
      const location = message.position ? `:${message.position.line}:${message.position.column}` : "";
      problem(source, `parse/import failure${location}`);
    }
    if (messages.length === 0) problem("<installed sources>", "parse/import check failed");
  }
}

if (problems.length) {
  for (const message of [...new Set(problems)]) console.error(`HOOK_LOAD_FAIL ${message}`);
  process.exitCode = 1;
} else {
  console.log(`HOOK_LOAD_OK entrypoints=${entrypoints.size}`);
}
