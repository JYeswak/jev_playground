import assert from "node:assert/strict";
import test from "node:test";
import { decideStop } from "./session-stop.ts";

test("missing demo continues once with context", () => {
  const result = decideStop({ stop_hook_active: false }, () => false);
  assert.equal(result.continue, true);
  assert.match(result.additionalContext, /demos\/consistency\/demo\.mjs/);
});

test("stop_hook_active does not continue", () => {
  assert.equal(decideStop({ stop_hook_active: true }, () => false), undefined);
});

test("aborted settle does not continue", () => {
  assert.equal(decideStop({ stop_hook_active: false, signal: { aborted: true } }, () => false), undefined);
});

test("present demos stay silent", () => {
  assert.equal(decideStop({ stop_hook_active: false }, () => true), undefined);
});
