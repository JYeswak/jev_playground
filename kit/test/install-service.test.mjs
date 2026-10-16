import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  assertSafeCommand,
  buildCanaryJob,
  buildDailyJob,
  buildDailyJobs,
  buildMinerJob,
  defaultSpecForFamilies,
  listDailyJobs,
  validateMinerJob,
} from "../src/install/daily-jobs.ts";
const FAMILIES = [
  { name: "classify" },
  { name: "rank" },
  { name: "verify" },
  { name: "score" },
  { name: "gate" },
];

function tempState() {
  return mkdtempSync(join(tmpdir(), "install-service-"));
}

test("emitted jobs carry label, schedule, command, off-switch, cap and keyless flag", () => {
  const stateDir = tempState();
  const jobs = buildDailyJobs(defaultSpecForFamilies(FAMILIES), { stateDir });
  assert.equal(jobs.length, 5);
  for (const job of jobs) {
    assert.match(job.label, /^classifier-(classify|rank|verify|score|gate)-eval-daily$/);
    assert.equal(job.schedule, "daily");
    assert.deepEqual(job.command.slice(0, 2), ["classifier", job.label.split("-")[1]]);
    assert.equal(job.command[job.command.length - 1], "eval");
    assert.equal(job.offSwitch, `${stateDir}/${job.label.split("-")[1]}.off`);
    assert.equal(job.timeCapSecs, 600);
    assert.equal(job.keylessSkip, true);
  }
});

test("re-running with identical inputs emits byte-identical definitions", () => {
  const stateDir = tempState();
  const once = JSON.stringify(buildDailyJobs(defaultSpecForFamilies(FAMILIES), { stateDir }));
  const twice = JSON.stringify(buildDailyJobs(defaultSpecForFamilies(FAMILIES), { stateDir }));
  assert.equal(once, twice);
  const shuffled = JSON.stringify(
    buildDailyJobs([...defaultSpecForFamilies(FAMILIES)].reverse(), { stateDir }),
  );
  assert.equal(once, shuffled);
});

test("job command with a repository path is refused", () => {
  assert.throws(() => assertSafeCommand(["classifier", "/Users/josh/Developer/jev/x", "eval"]), /repository path/);
  assert.throws(() => assertSafeCommand(["classifier", "gate/../evil", "eval"]), /repository path/);
});

test("skill-gap extraction schedule is refused", () => {
  const stateDir = tempState();
  assert.throws(
    () => buildDailyJob({ family: "classify", schedule: "daily", kind: "skill-gap" }, { stateDir }),
    /belongs to omp-kit/,
  );
});
test("launchctl in a command is refused; module never shells out", () => {
  assert.throws(() => assertSafeCommand(["launchctl", "load", "x"]), /service-manager/);
  const source = readFileSync(new URL("../src/install/daily-jobs.ts", import.meta.url), "utf8");
  for (const banned of ["child_process", "execFile", "execSync", "spawnSync", "spawn("]) {
    assert.ok(!source.includes(banned), `module must not contain ${banned}`);
  }
});

test("duplicate family labels are refused", () => {
  const stateDir = tempState();
  assert.throws(
    () =>
      buildDailyJobs(
        [
          { family: "gate", schedule: "daily" },
          { family: "gate", schedule: "daily" },
        ],
        { stateDir },
      ),
    /duplicate job label/,
  );
});

test("canary job wraps the fixed runner, not an inline shell string", () => {
  const stateDir = tempState();
  const job = buildCanaryJob({ stateDir });
  assert.equal(job.label, "classifier-canary-daily");
  assert.deepEqual(job.command, ["scripts/jev-latest-canary-run.sh"]);
  assert.equal(job.keylessSkip, true);
  assert.equal(job.offSwitch, `${stateDir}/canary.off`);
  for (const token of job.command) {
    assert.ok(!token.includes("zsh"), "no inline shell wrapper");
  }
});

test("miner job carries the fixed cap and load deferral", () => {
  const stateDir = tempState();
  const job = buildMinerJob({ stateDir });
  assert.equal(job.label, "classifier-miner-daily");
  assert.deepEqual(job.command, ["nice", "-n", "10", "python3", "work/fleet-schema/miner.py", "--daily", "--json"]);
  assert.equal(job.timeCapSecs, 3000);
  assert.equal(job.deferWhileLoadAbove, 80);
  assert.equal(job.keylessSkip, true);
  validateMinerJob(job);
  assert.throws(() => validateMinerJob({ ...job, timeCapSecs: 600 }), /without the 3,000 s time cap/);
  assert.throws(() => validateMinerJob({ ...job, deferWhileLoadAbove: undefined }), /without the load-80 deferral/);
});

test("plain relative runner paths pass; absolute and traversal paths refuse", () => {
  assert.doesNotThrow(() => assertSafeCommand(["work/fleet-schema/miner.py", "--daily"]));
  assert.doesNotThrow(() => assertSafeCommand(["scripts/jev-latest-canary-run.sh"]));
  assert.throws(() => assertSafeCommand(["/abs/path/x"]), /repository path/);
  assert.throws(() => assertSafeCommand(["a/../../evil"]), /repository path/);
  assert.throws(() => assertSafeCommand(["systemctl", "start", "x"]), /service-manager/);
});

test("dry-run listing composes evals, canary and miner without writing", () => {
  const stateDir = tempState();
  const jobs = listDailyJobs(
    [{ name: "classify" }, { name: "gate" }],
    { stateDir },
  );
  assert.deepEqual(
    jobs.map((job) => job.label),
    ["classifier-canary-daily", "classifier-classify-eval-daily", "classifier-gate-eval-daily", "classifier-miner-daily"],
  );
});
