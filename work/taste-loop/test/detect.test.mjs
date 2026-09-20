import test from "node:test";
import assert from "node:assert/strict";
import {
  isWriteTool,
  isUserFacingPath,
  isUserFacingWrite,
  copyClass,
  regexCatchesHeckle,
  hasDestructiveVerb,
  hasWayBack,
  isOnboardingPath,
  hasSkipExit,
  hasPreselection,
  looksLikeForm,
  isFirstLookPath,
  extractHeadlinesAndCtas,
  filePathFromEvent,
  contentFromEvent,
} from "../src/detect.mjs";

test("write-tool set is closed: unknown tools are not writes", () => {
  assert.equal(isWriteTool("write"), true);
  assert.equal(isWriteTool("edit"), true);
  assert.equal(isWriteTool("apply_patch"), true);
  assert.equal(isWriteTool("ast_edit"), true);
  assert.equal(isWriteTool("bash"), false);
  assert.equal(isWriteTool("read"), false);
  assert.equal(isWriteTool(undefined), false);
});

test("user-facing paths exclude tests, dist, and node_modules", () => {
  assert.equal(isUserFacingPath("src/routes/index.tsx"), true);
  assert.equal(isUserFacingPath("src/app/page.tsx"), true);
  assert.equal(isUserFacingPath("README.md"), true);
  assert.equal(isUserFacingPath("src/routes/index.test.tsx"), false);
  assert.equal(isUserFacingPath("src/foo.spec.ts"), false);
  assert.equal(isUserFacingPath("node_modules/foo/index.js"), false);
  assert.equal(isUserFacingPath("dist/index.js"), false);
  assert.equal(isUserFacingPath("src/lib/hash.rs"), false);
  assert.equal(isUserFacingPath(""), false);
  assert.equal(isUserFacingPath(undefined), false);
});

test("heckle planted class: dead strings match, ordinary copy does not", () => {
  assert.equal(copyClass("An error occurred."), "error");
  assert.equal(copyClass("Something went wrong"), "error");
  assert.equal(copyClass("No data"), "empty");
  assert.equal(copyClass("Loading..."), "loading");
  assert.equal(copyClass("Couldn't save. Retry?"), "other");
  assert.equal(regexCatchesHeckle("An error occurred"), true);
  assert.equal(regexCatchesHeckle("Couldn't save. Retry?"), false);
});

test("destructive verb and way-back are independent", () => {
  assert.equal(hasDestructiveVerb("Delete account"), true);
  assert.equal(hasWayBack("Delete account"), false);
  assert.equal(hasWayBack("Delete account. Cancel keeps it."), true);
  assert.equal(hasDestructiveVerb("Save draft"), false);
});

test("onboarding path and skip-exit", () => {
  assert.equal(isOnboardingPath("src/onboarding/tour.tsx"), true);
  assert.equal(isOnboardingPath("src/routes/index.tsx"), false);
  assert.equal(hasSkipExit("Skip for now"), true);
  assert.equal(hasSkipExit("Continue"), false);
});

test("preselection and form detectors", () => {
  assert.equal(hasPreselection("defaultChecked={true}"), true);
  assert.equal(hasPreselection("<input type='checkbox' />"), false);
  assert.equal(looksLikeForm("<input name='email' />"), true);
  assert.equal(looksLikeForm("<p>Hello</p>"), false);
});

test("first-look paths are index/home/page, not settings", () => {
  assert.equal(isFirstLookPath("src/routes/index.tsx"), true);
  assert.equal(isFirstLookPath("src/app/page.tsx"), true);
  assert.equal(isFirstLookPath("src/routes/settings.tsx"), false);
});

test("event path/content readers tolerate several omp shapes", () => {
  assert.equal(filePathFromEvent({ input: { path: "a.tsx" } }), "a.tsx");
  assert.equal(filePathFromEvent({ input: { file_path: "b.tsx" } }), "b.tsx");
  assert.equal(contentFromEvent({ input: { content: "hello" } }), "hello");
  assert.equal(contentFromEvent({ input: { new_string: "x" } }), "x");
  assert.equal(filePathFromEvent({ toolName: "write", input: {} }), undefined);
  assert.equal(isUserFacingWrite({ toolName: "write", input: { path: "src/app/page.tsx", content: "x" } }), true);
  assert.equal(isUserFacingWrite({ toolName: "bash", input: { path: "src/app/page.tsx" } }), false);
});

test("headline/CTA extract does not throw on empty", () => {
  assert.deepEqual(extractHeadlinesAndCtas(""), { headlines: [], ctas: [] });
  const { headlines, ctas } = extractHeadlinesAndCtas("<h1>Payroll in one click</h1><button>Export CSV</button>");
  assert.deepEqual(headlines, ["Payroll in one click"]);
  assert.deepEqual(ctas, ["Export CSV"]);
});
