/**
 * Fixture structure recovery (cookbook shape, FIXTURE SCORING).
 * Pass 1: stitch hard-wrapped lines — join line i into i-1 iff line i-1 does
 * not end with terminal punctuation (.?!:), neither side is a list item, and
 * the pair is not gap-separated. (Stand-in for the per-pair "picks up
 * mid-sentence" Noul.)
 * Pass 2: classify each stitched block — warning, list item, code (line
 * starts with a command token), heading (short, no terminal mark), else
 * paragraph. (Stand-in for the per-block Choice.)
 */
const TERMINAL = /[.?!:]\s*$/;
const CODE_HINT = /^\s*(\$|bun |npm |git |make |node |python |cargo |docker |cd |ls )/;
const WARN_HINT = /\b(warn|warning|note|caution|important)\b/i;
const LIST_HINT = /^\s*(?:[-*]|\d+[.)])\s+/;

export const RAW = [
  "Migration to the new build system",
  "",
  "Hi everyone, quick heads up about the build system migration that is",
  "happening next week. We have been running the new pipeline in shadow",
  "mode for three weeks and the results look solid.",
  "",
  "What changes for you",
  "",
  "The old make targets keep working until the end of the month.",
  "bun run build",
  "",
  "Warning: the old pipeline stops on Friday, so migrate before then.",
  "",
  "- back up the lockfile first",
  "- run the migrator on staging",
  "Generated artifacts no longer need to be committed.",
];

export function stitch(lines) {
  const out = [];
  for (const line of lines) {
    if (line === "") { out.push({ text: "", gap: true }); continue; }
    const prev = out.length ? out[out.length - 1] : null;
    const startsList = LIST_HINT.test(line);
    const prevIsList = prev && !prev.gap && LIST_HINT.test(prev.text);
    if (prev && !prev.gap && !TERMINAL.test(prev.text) && !startsList && !prevIsList) {
      prev.text += " " + line;
      prev.joins = (prev.joins || 0) + 1;
    } else {
      out.push({ text: line, gap: false });
    }
  }
  return out;
}

export function classify(block) {
  const t = block.text;
  if (WARN_HINT.test(t)) return "warning";
  if (LIST_HINT.test(t)) return "list";
  if (CODE_HINT.test(t)) return "code";
  if (t.length < 60 && !TERMINAL.test(t)) return "heading";
  return "paragraph";
}

export function render(blocks) {
  return blocks.map(({ text, kind }) => {
    if (kind === "heading") return `## ${text}`;
    if (kind === "code") return "```\n" + text + "\n```";
    if (kind === "warning") return `> ${text.replace(/^warning:\s*/i, "")}`;
    if (kind === "list") return text.startsWith("-") || LIST_HINT.test(text) ? text : `- ${text}`;
    if (text === "") return "";
    return text;
  }).join("\n");
}

export function recover(lines = RAW) {
  const stitched = stitch(lines).filter((b) => !(b.gap && b.text === ""));
  const blocks = stitched.map((b) => (b.text === "" ? { ...b, kind: "blank" } : { ...b, kind: classify(b) }));
  return { blocks, markdown: render(blocks), joins: blocks.reduce((n, b) => n + (b.joins || 0), 0) };
}
