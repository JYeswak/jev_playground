/**
 * Shared detectors for the taste-loop packages.
 *
 * WHY THIS EXISTS. Eleven observe-only extensions would otherwise each invent
 * "is this a user-facing write". A detector invented eleven times drifts; a
 * detector invented once can be tested once. Regex gates live HERE so a
 * question that a rule already answers never reaches Jev (harm-rule lesson).
 *
 * This module never calls Jev. It never throws on bad input. Every function
 * returns a conservative no when the event is unreadable.
 */

export const WRITE_TOOLS = new Set(["write", "edit", "apply_patch", "ast_edit"]);

const USER_FACING_EXT =
  /\.(tsx|jsx|vue|svelte|html|css|mdx)$/i;
const USER_FACING_TS =
  /(^|\/)(components|pages|routes|app|ui|views|screens|layouts)\//;
const MARKDOWN = /\.(md|mdx)$/i;
const NOT_USER_FACING =
  /(^|\/)(test|tests|__tests__|node_modules|dist|\.omp)(\/|$)|(\.test\.|\.spec\.)/i;

const ERROR_COPY =
  /\b(an error occurred|something went wrong|unexpected error|internal server error|unhandled|undefined is not)\b/i;
const EMPTY_COPY =
  /\b(no data|nothing here|no items|no results|empty state|you have no)\b/i;
const LOADING_COPY =
  /\b(loading(\.\.\.)?|please wait|fetching|spinner)\b/i;
const DESTRUCTIVE =
  /\b(delete|remove|reset|disconnect|unlink|destroy|archive|wipe|revoke)\b/i;
const WAY_BACK =
  /\b(undo|cancel|restore|never mind|go back|keep it|don't|revert)\b/i;
const SKIP_EXIT =
  /\b(skip|not now|later|maybe later|no thanks)\b/i;
const ONBOARDING_PATH =
  /(onboard|welcome|tour|wizard|getting[-_]?started|first[-_]?run)/i;
const PRESELECT =
  /\b(defaultChecked|defaultValue|defaultSelected|pre[- ]?tick|pre[- ]?select|selected:\s*true)\b/;
const PLACEHOLDER_AS_LABEL =
  /\bplaceholder\s*[:=]\s*['"`][^'"`]{1,40}['"`]/i;
const CLICK_HERE =
  /\b(click here|learn more|read more)\b/i;

export function isWriteTool(tool) {
  return WRITE_TOOLS.has(String(tool ?? ""));
}

export function toolName(event) {
  return String(event?.toolName ?? event?.name ?? "");
}

export function toolCallId(event) {
  return typeof event?.toolCallId === "string" ? event.toolCallId : null;
}

export function inputOf(event) {
  const input = event?.input;
  return input && typeof input === "object" ? input : {};
}

export function filePathFromEvent(event) {
  const input = inputOf(event);
  for (const key of ["path", "file_path", "filePath", "dst", "filename"]) {
    const value = input[key];
    if (typeof value === "string" && value.length > 0) return value;
  }
  if (typeof event?.path === "string") return event.path;
  return undefined;
}

export function contentFromEvent(event) {
  const input = inputOf(event);
  for (const key of ["content", "new_string", "newString", "newText", "new_text", "text"]) {
    const value = input[key];
    if (typeof value === "string" && value.length > 0) return value;
  }
  if (typeof input.patch === "string") return input.patch;
  return undefined;
}

export function isUserFacingPath(path) {
  if (typeof path !== "string" || path.length === 0) return false;
  if (NOT_USER_FACING.test(path)) return false;
  if (USER_FACING_EXT.test(path)) return true;
  if (MARKDOWN.test(path) && /(^|\/)(readme|docs\/|changelog)/i.test(path)) return true;
  if (/\.(ts|js)$/i.test(path) && USER_FACING_TS.test(path)) return true;
  return false;
}

export function isUserFacingWrite(event) {
  return isWriteTool(toolName(event)) && isUserFacingPath(filePathFromEvent(event));
}

/** error | empty | loading | other — planted-class gate for heckle. */
export function copyClass(text) {
  const s = String(text ?? "");
  if (ERROR_COPY.test(s)) return "error";
  if (EMPTY_COPY.test(s)) return "empty";
  if (LOADING_COPY.test(s)) return "loading";
  return "other";
}

export function regexCatchesHeckle(text) {
  return copyClass(text) !== "other";
}

export function hasDestructiveVerb(text) {
  return DESTRUCTIVE.test(String(text ?? ""));
}

export function hasWayBack(text) {
  return WAY_BACK.test(String(text ?? ""));
}

export function isOnboardingPath(path) {
  return ONBOARDING_PATH.test(String(path ?? ""));
}

export function hasSkipExit(text) {
  return SKIP_EXIT.test(String(text ?? ""));
}

export function hasPreselection(text) {
  return PRESELECT.test(String(text ?? ""));
}

export function looksLikeForm(text) {
  return /<(input|textarea|select)\b/i.test(String(text ?? "")) ||
    /\b(placeholder|label|helperText|errorMessage)\b/.test(String(text ?? ""));
}

export function placeholderAsLabel(text) {
  return PLACEHOLDER_AS_LABEL.test(String(text ?? ""));
}

export function vagueAffordance(text) {
  return CLICK_HERE.test(String(text ?? ""));
}

/** First-look files: landing, home, index, app shell. */
export function isFirstLookPath(path) {
  const p = String(path ?? "").toLowerCase();
  if (!isUserFacingPath(p)) return false;
  return /(^|\/)(index|home|landing|app|page|welcome)\.[a-z]+$/.test(p) ||
    /(routes\/index|pages\/index|src\/app\/page)/.test(p);
}

export function extractHeadlinesAndCtas(text) {
  const s = String(text ?? "");
  const headlines = [];
  const ctas = [];
  const h = s.matchAll(/<(h1|h2)[^>]*>([^<]{1,120})/gi);
  for (const m of h) headlines.push(m[2].trim());
  const buttons = s.matchAll(/<(button|a)[^>]*>([^<]{1,80})/gi);
  for (const m of buttons) ctas.push(m[2].trim());
  const jsx = s.matchAll(/>\s*\{?['"`]([A-Z][^'"`]{1,60})['"`]\s*\}?\s*</g);
  for (const m of jsx) {
    if (/^(Delete|Remove|Save|Continue|Get started|Sign up|Log in|Export)/i.test(m[1])) {
      ctas.push(m[1]);
    }
  }
  return { headlines, ctas };
}

export function clip(text, n = 4000) {
  const s = String(text ?? "");
  return s.length <= n ? s : s.slice(0, n);
}
