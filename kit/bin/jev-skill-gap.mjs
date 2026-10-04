#!/usr/bin/env node
import { homedir } from "node:os";
import { resolve } from "node:path";
import {
  installLaunchAgent,
  resolveInfisicalBinary,
  runDailyMiner,
} from "../dist/skill-gap.js";

function option(args, name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
}

function print(value, robot) {
  process.stdout.write(`${robot ? JSON.stringify(value) : JSON.stringify(value, null, 2)}\n`);
}

function help() {
  process.stdout.write(
    "Usage: jev-skill-gap --daily [--repo-root PATH] [--home PATH] [--state-dir PATH] [--model ID] [--no-review-beads] [--robot]\n" +
    "       jev-skill-gap --install [--repo-root PATH] [--home PATH] [--infisical PATH] [--robot]\n",
  );
}

async function main(args) {
  const robot = args.includes("--robot");
  if (args.includes("--help") || args.includes("-h")) {
    help();
    return 0;
  }
  const repoRoot = resolve(option(args, "--repo-root") ?? process.cwd());
  const home = resolve(option(args, "--home") ?? process.env.HOME ?? homedir());

  if (args.includes("--install")) {
    const infisicalPath = option(args, "--infisical") ?? resolveInfisicalBinary(home);
    if (!infisicalPath) {
      print({ status: "NOT_RUN", reason: "infisical-binary-unavailable" }, robot);
      return 2;
    }
    const result = await installLaunchAgent({
      home,
      repoRoot,
      nodePath: process.execPath,
      infisicalPath,
    });
    print(result, robot);
    return result.status === "INSTALLED" || result.status === "ALREADY_LOADED" ? 0 : 1;
  }

  if (!args.includes("--daily")) {
    help();
    return 2;
  }
  const report = await runDailyMiner({
    home,
    repoRoot,
    stateDir: option(args, "--state-dir"),
    model: option(args, "--model"),
    dryRun: args.includes("--no-review-beads"),
  });
  print(report, robot);
  return report.status === "OK" ? 0 : report.status === "NOT_RUN" ? 2 : 1;
}

main(process.argv.slice(2)).then((code) => {
  process.exitCode = code;
}).catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  print({ status: "ERROR", error: message }, process.argv.includes("--robot"));
  process.exitCode = 1;
});
