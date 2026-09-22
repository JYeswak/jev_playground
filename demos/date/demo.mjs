#!/usr/bin/env node
// Riff on the official date-extraction cookbook. Keyless by default: six
// fixture documents with recorded part answers, so the calendar math runs
// with no key.
// `node demos/date/demo.mjs --live` asks through work/jev-client.
// Official shape: docs-mirror/typesafe/cookbooks/date_extraction_cookbook.md
// (seven Choice questions read a date's shape and parts; code assembles them
// into a date, fills a missing year, resolves weekday math, and routes anything
// under confidence 0.60 — or unassemblable — to a human).
// NO-CLAIM: a fixture date is not a live extraction.

const TODAY = { y: 2026, m: 7, d: 30 }; // fixed Thursday; relative dates reproduce
const REVIEW_BELOW = 0.60;
const MONTHS = {
  January: 1, February: 2, March: 3, April: 4, May: 5, June: 6,
  July: 7, August: 8, September: 9, October: 10, November: 11, December: 12,
};
const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const EXAMPLES = [
  {
    role: "the date the agreement takes effect",
    document: "This agreement is effective January 1, 2025 and expires December 31, 2027.",
    expected: "2025-01-01",
    recorded: {
      mode: ["absolute", 0.97], month: ["January", 0.98], day: ["1", 0.99],
      year: ["2025", 0.97], day_anchor: ["none", 0.99], weekday: ["none", 0.99],
      week_offset: ["none", 0.99],
    },
  },
  {
    role: "the date the agreement expires",
    document: "This agreement is effective January 1, 2025 and expires December 31, 2027.",
    expected: "2027-12-31",
    recorded: {
      mode: ["absolute", 0.91], month: ["December", 0.95], day: ["31", 0.96],
      year: ["2027", 0.93], day_anchor: ["none", 0.99], weekday: ["none", 0.99],
      week_offset: ["none", 0.99],
    },
  },
  {
    role: "the deadline to return the form",
    document: "Please return the signed form by August 14.",
    expected: "2026-08-14",
    recorded: {
      mode: ["absolute", 0.95], month: ["August", 0.97], day: ["14", 0.98],
      year: ["none", 0.95], day_anchor: ["none", 0.99], weekday: ["none", 0.99],
      week_offset: ["none", 0.99],
    },
  },
  {
    role: "the date of the kickoff call",
    document: "Please return the signed form by August 14.",
    expected: null,
    recorded: {
      mode: ["absolute", 0.46], month: ["none", 0.50], day: ["none", 0.52],
      year: ["none", 0.60], day_anchor: ["none", 0.99], weekday: ["none", 0.99],
      week_offset: ["none", 0.99],
    },
  },
  {
    role: "the date the survey closes",
    document: "Heads up - the customer survey closes today at 5pm.",
    expected: "2026-07-30",
    recorded: {
      mode: ["relative", 0.94], month: ["none", 0.99], day: ["none", 0.99],
      year: ["none", 0.99], day_anchor: ["today", 0.96], weekday: ["none", 0.99],
      week_offset: ["none", 0.99],
    },
  },
  {
    role: "the date of the design review",
    document: "Let's schedule the design review for next Thursday.",
    expected: "2026-08-06",
    recorded: {
      mode: ["relative", 0.92], month: ["none", 0.99], day: ["none", 0.99],
      year: ["none", 0.99], day_anchor: ["weekday", 0.94], weekday: ["Thursday", 0.95],
      week_offset: ["next", 0.93],
    },
  },
];

const EXPECT = Object.fromEntries(EXAMPLES.map((e) => [e.role, e.expected]));

function iso(y, m, d) {
  return `${String(y).padStart(4, "0")}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
}
function daysInMonth(y, m) {
  return new Date(Date.UTC(y, m, 0)).getUTCDate();
}
function addDays(base, n) {
  const t = Date.UTC(base.y, base.m - 1, base.d) + n * 86400000;
  const d = new Date(t);
  return { y: d.getUTCFullYear(), m: d.getUTCMonth() + 1, d: d.getUTCDate() };
}
function weekdayIdx(name) {
  return WEEKDAYS.indexOf(name);
}
function resolveWeekday(today, weekday, weekOffset) {
  const w = weekdayIdx(weekday);
  const mondayDow = ((new Date(Date.UTC(today.y, today.m - 1, today.d)).getUTCDay() + 6) % 7);
  const thisMonday = addDays(today, -mondayDow);
  if (weekOffset === "next") return addDays(thisMonday, 7 + w);
  if (weekOffset === "current") return addDays(thisMonday, w);
  const todayDow = ((new Date(Date.UTC(today.y, today.m - 1, today.d)).getUTCDay() + 6) % 7);
  return addDays(today, (w - todayDow + 7) % 7);
}

function assemble(parts, today = TODAY) {
  const mode = parts.mode.choice;
  const confs = [parts.mode.confidence];
  const result = (resolved, note) => {
    const usable = confs.filter((c) => c !== null && c !== undefined);
    const confidence = usable.length > 0 ? Math.min(...usable) : null;
    return {
      date: resolved,
      confidence,
      needs_review: resolved === null || confidence === null || confidence < REVIEW_BELOW,
      note,
    };
  };
  if (mode === "none") return result(null, "no such date stated");
  if (mode === "absolute") {
    const month = parts.month.choice, day = parts.day.choice, year = parts.year.choice;
    confs.push(parts.month.confidence, parts.day.confidence, parts.year.confidence);
    if (month === "none" || day === "none" || !/^\d+$/.test(day) || !(month in MONTHS)) {
      return result(null, "absolute date incomplete");
    }
    if (year === "out_of_range") return result(null, "year outside 1900-2050");
    const m = MONTHS[month], dd = parseInt(day, 10);
    if (dd < 1 || dd > daysInMonth(year === "none" ? today.y : parseInt(year, 10), m)) {
      return result(null, `impossible date: ${month} ${day}`);
    }
    if (year === "none") {
      let resolved = { y: today.y, m, d: dd };
      const past = (today.y - resolved.y) * 372 + (today.m - resolved.m) * 31 + (today.d - resolved.d);
      if (past > 31) resolved = { y: today.y + 1, m, d: dd };
      return result(iso(resolved.y, resolved.m, resolved.d), "");
    }
    return result(iso(parseInt(year, 10), m, dd), "");
  }
  if (mode === "relative") {
    const anchor = parts.day_anchor.choice;
    confs.push(parts.day_anchor.confidence);
    if (anchor === "today") return result(iso(today.y, today.m, today.d), "");
    if (anchor === "tomorrow") { const r = addDays(today, 1); return result(iso(r.y, r.m, r.d), ""); }
    if (anchor === "day_after") { const r = addDays(today, 2); return result(iso(r.y, r.m, r.d), ""); }
    if (anchor === "weekday") {
      const weekday = parts.weekday.choice, offset = parts.week_offset.choice;
      confs.push(parts.weekday.confidence, parts.week_offset.confidence);
      if (!(weekday in Object.fromEntries(WEEKDAYS.map((w) => [w, 1])))) {
        return result(null, "relative weekday not read");
      }
      const r = resolveWeekday(today, weekday, offset);
      return result(iso(r.y, r.m, r.d), "");
    }
    return result(null, "relative day not read");
  }
  return result(null, `unrecognized mode: ${mode}`);
}

function dateQuestions(role) {
  const absent = "The document does not state this, or it is not this kind of date.";
  const months = {};
  for (const m of Object.keys(MONTHS)) months[m] = null;
  months.none = absent;
  const days = {};
  for (let d = 1; d <= 31; d++) days[String(d)] = null;
  days.none = absent;
  const years = {};
  for (let y = 1900; y <= 2050; y++) years[String(y)] = null;
  years.out_of_range = "A year is stated for this date but is outside the listed range.";
  years.none = "No year is stated for this date.";
  const weekdays = {};
  for (const w of WEEKDAYS) weekdays[w] = null;
  weekdays.none = absent;
  return {
    mode: { type: "choice", instructions: `How is ${role} written? 'absolute' = a calendar date naming a month; 'relative' = given relative to today; 'none' = the document does not state this date.`, criteria: { absolute: null, relative: null, none: null } },
    month: { type: "choice", instructions: `If ${role} is an absolute calendar date, which month is it in?`, criteria: months },
    day: { type: "choice", instructions: `If ${role} is an absolute calendar date, which day of the month (1-31)?`, criteria: days },
    year: { type: "choice", instructions: `If ${role} is an absolute calendar date, which year?`, criteria: years },
    day_anchor: { type: "choice", instructions: `If ${role} is relative to today, which day is it?`, criteria: { today: null, tomorrow: null, day_after: null, weekday: null, none: absent } },
    weekday: { type: "choice", instructions: `If ${role} names a day of the week, which one?`, criteria: weekdays },
    week_offset: { type: "choice", instructions: `If ${role} names a weekday, which week is it in?`, criteria: { current: null, next: null, none: absent } },
  };
}

async function readPartsLive(document, role) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  const r = await askJevBundle({
    model: "jev-1.13.0",
    state: { document, role },
    questions: dateQuestions(role),
    timeoutMs: 30000,
  });
  if (!r.ok) {
    console.error(`live call failed: ${r.reason} ${r.error}`);
    process.exit(2);
  }
  const parts = {};
  for (const [part, ans] of Object.entries(r.answers)) {
    parts[part] = { choice: ans.choice, confidence: ans.confidence };
  }
  return parts;
}

function partsOf(example) {
  const parts = {};
  for (const [part, [choice, confidence]] of Object.entries(example.recorded)) {
    parts[part] = { choice, confidence };
  }
  return parts;
}

const live = process.argv.includes("--live");
console.log("datemap  official shape: docs-mirror/typesafe/cookbooks/date_extraction_cookbook.md");
console.log("");
console.log(`${"".padEnd(3)}${"question".padEnd(38)}${"expected".padEnd(12)}${"got".padEnd(12)}${"conf".padStart(6)}  flags`);
console.log("-".repeat(84));
let failed = 0;
for (const example of EXAMPLES) {
  const parts = live ? await readPartsLive(example.document, example.role) : partsOf(example);
  const r = assemble(parts);
  const got = r.date ?? "none";
  const exp = example.expected ?? "none";
  const mark = got === exp ? "OK" : "XX";
  if (mark === "XX") failed = 1;
  const conf = r.confidence === null ? "   n/a" : r.confidence.toFixed(2).padStart(6);
  let flags = r.needs_review ? "  <== review" : "";
  if (r.note) flags += `  (${r.note})`;
  console.log(`${mark.padEnd(3)}${example.role.padEnd(38)}${exp.padEnd(12)}${got.padEnd(12)}${conf}${flags}`);
}
console.log("");
console.log(live ? "live lane: scored through askJevBundle." : "fixture lane: recorded parts, no API call. --live spends a key.");
process.exit(failed ? 1 : 0);
