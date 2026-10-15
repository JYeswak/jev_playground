import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  assertSafeCommand,
  buildDailyJob,
  buildDailyJobs,
  defaultSpecForFamilies,
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
