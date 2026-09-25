#!/usr/bin/env python3
"""Which omp-jev-* surfaces are loaded, and which have real decision rows.

Keyless. One row per work/omp-jev-* package. A row counts only after its JSON
line parses. Real work is a session whose path and cwd are not a probe or test
session. The rule is the one jev-cz0 used: /tmp, review-l3, probe, and fixture
sessions are not real work.

    python3 work/omp-jev-review/surface-census.py               # surfaces, then judge-role
    python3 work/omp-jev-review/surface-census.py --judge       # judge-role section only
    python3 work/omp-jev-review/surface-census.py --fleet-line  # three lines, last 24h

Judge role (bead jev-xpk1): omp answers find, auto-thinking, eval judge()/judge_batch() and
unexpected-stop detection with the `judge` model role, pinned fleet-wide to typesafe/jev-latest
with no fallback (jev-m1e9). It writes one `model_usage` row per judge request into the session
file, failed requests included: a planted failure (TYPESAFE_BASE_URL=http://127.0.0.1:9,
2026-09-25) wrote `stopReason: "error"` plus `errorMessage: "Unable to connect. ..."` with zero
usage, one row per failed request. So a failure count here is a measurement, not an absence.

Skills (bead jev-yy7f): the second --fleet-line line counts skill reads in the same session files,
probe sessions excluded: a `read` tool call of skill://<name>[/...] or of a path under
.claude/skills/<name>/ or .agents/skills/<name>/; a `bash` call where such a file is an argument
of a file reader (cat, sed, head, grep, ... or `python -c` with open()/read()), never a path that
only sits inside a message string (ntm send, br comments, git -m); an `eval` cell whose code calls
read(, tool.read( or open( on a skill path or skill://<name>; and the `skill-prompt` row omp writes
when a user invokes /skill:<name>. A call whose toolResult is `isError: true` ("Unknown skill" in
a pane older than the install) is not a read. It names how many skills in
~/.claude/skills/THIRD-PARTY-SKILLS.tsv were read at least once; no ledger is NOT_RUN.

Key exposure (bead jev-9ov4): the third --fleet-line line counts session .jsonl files under both
session roots modified in the last 24h, probe sessions included, that hold an unmarked string
matching a `type: regex` entry of .omp/secrets.yml (the TypeSafe key shape; read from there, never
copied here), and names the newest 3 paths with their mtimes. It prints paths only, never the
match. A match whose segment after the first `_` starts with FAKE_MARKER (`fakefake`) is a fake
one of our tools made (scripts/omp-secret-probe.py fake_key()); a file holding only such matches
is counted apart as "hold only marked fakes" and never pages. Unmarked fakes written before the
marker existed (2026-09-25) stay in the count until their files age out of the 24h window. A
missing or unparsable secrets.yml, or no session files, is NOT_RUN. Why: 2026-09-25 05:57Z a pane
printed the live key into a tool result, omp's session log stored it, and a manual scan found it
50 minutes later; scripts/fleet-idle-watch.py pages pane 1 once per new path.

Exit 0 always. This is a census, not a gate.
"""

import ast
import json
import os
import re
import shlex
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parents[2]
TYPE_RE = re.compile(r"com\.zeststream\.[A-Za-z0-9_.-]+")
CREDITS_AFTER = "2026-09-24T04:19:00Z"
JUDGE_PROVIDER = "typesafe"
SESSION_ROOTS = "~/.omp/agent/sessions, ~/.omp/profiles/*/agent/sessions"
SECRETS = REPO / ".omp" / "secrets.yml"
KEY_NEWEST = 3
FAKE_MARKER = b"fakefake"
REGEX_LITERAL = re.compile(r"^/(.+)/([a-z]*)$", re.S)
REGEX_FLAGS = {"i": re.I, "m": re.M, "s": re.S}
SKILL_LEDGER = HOME / ".claude" / "skills" / "THIRD-PARTY-SKILLS.tsv"
SKILL_NAME = r"[A-Za-z0-9._-]+"
SKILL_URL_RE = re.compile(rf"^skill://({SKILL_NAME})")
SKILL_DIR_RE = re.compile(rf"/\.(?:claude|agents)/skills/({SKILL_NAME})/")
SKILL_FILE_RE = re.compile(rf"/\.(?:claude|agents)/skills/({SKILL_NAME})/[^/\s]")
CODE_READ_RE = re.compile(
    r"""\b(?:read|open)\(\s*(?:\{\s*["']?path["']?\s*:\s*|path\s*=\s*)?(["'`])([^"'`\n]+)\1"""
)
BASH_READERS = frozenset(
    "cat sed head tail less more bat grep egrep fgrep rg awk wc nl".split()
)
BASH_WRAPPERS = frozenset("sudo env time command nohup nice".split())
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
SKILL_PROMPT_RE = re.compile(rf'^\[IMPORTANT: User invoked the "({SKILL_NAME})" skill')


def skill_of_path(path):
    """The skill a read path names: skill://<name>[...] or .claude|.agents/skills/<name>/..."""
    match = SKILL_URL_RE.match(path)
    if match is None:
        match = SKILL_DIR_RE.search(path)
    return match.group(1) if match else None


def code_skills(code, language):
    """Skills a code cell reads with read(, tool.read( or open( on a literal path.

    Python is parsed, so a read call that only sits inside a string literal is not a read; a
    cell Python cannot parse (IPython magics) and JS fall back to CODE_READ_RE over the text.
    """
    if language == "py":
        flags = ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
        try:
            tree = compile(code, "<cell>", "exec", flags)
        except (SyntaxError, ValueError):
            tree = None
        if tree is not None:
            return {n for p in python_read_paths(tree) if (n := skill_of_path(p))}
    return {n for _q, p in CODE_READ_RE.findall(code) if (n := skill_of_path(p))}


def python_read_paths(tree):
    """Literal paths passed to read(...)/x.read(...)/open(...) calls, incl. read({'path': ...})."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name not in ("read", "open"):
            continue
        values = node.args[:1] + [k.value for k in node.keywords if k.arg == "path"]
        for value in values:
            if isinstance(value, ast.Dict):
                value = next(
                    (
                        v
                        for k, v in zip(value.keys, value.values)
                        if isinstance(k, ast.Constant) and k.value == "path"
                    ),
                    None,
                )
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                yield value.value


def bash_skills(command):
    """Skills whose files are arguments of a file reader in a shell command.

    Words come from shlex, so a quoted message (ntm send '...', br comments add "...") is one
    argument of a command that is not a reader. Unparseable commands count nothing.
    """
    lex = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lex.whitespace = " \t\r"
    try:
        words = list(lex)
    except ValueError:
        return set()
    found, simple = set(), []
    for word in words + [";"]:
        if word != "\n" and not (word and set(word) <= set(";&|()")):
            simple.append(word)
            continue
        i = 0
        while i < len(simple) and (
            simple[i] in BASH_WRAPPERS or ASSIGNMENT_RE.match(simple[i])
        ):
            i += 1
        program = simple[i].rsplit("/", 1)[-1] if i < len(simple) else ""
        args = simple[i + 1 :]
        if program in BASH_READERS:
            found.update(m.group(1) for a in args if (m := SKILL_FILE_RE.search(a)))
        elif program.startswith("python") and "-c" in args[:-1]:
            found.update(code_skills(args[args.index("-c") + 1], "py"))
        simple = []
    return found


def packages():
    root = REPO / "work"
    return sorted(
        p.name for p in root.iterdir() if p.is_dir() and p.name.startswith("omp-jev-")
    )


def short_name(package):
    return package.removeprefix("omp-jev-")


def decision_types(package):
    found = set()
    root = REPO / "work" / package
    if not root.is_dir():
        return []
    for path in root.rglob("*"):
        if path.suffix not in {".ts", ".mjs", ".js"} or "node_modules" in path.parts:
            continue
        if "/test/" in str(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in TYPE_RE.findall(text):
            if token.endswith(".decision.v1") or token.endswith(".screen.v1"):
                found.add(token)
    return sorted(found)


def config_files():
    files = [REPO / ".omp" / "config.yml", HOME / ".omp" / "agent" / "config.yml"]
    files.extend(HOME.glob(".omp/profiles/*/agent/config.yml"))
    return [p for p in files if p.is_file()]


def listed_extensions(config_path):
    listed = []
    in_list = False
    for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped in {"extensions:", "tools:"}:
            in_list = True
            continue
        if in_list and stripped.startswith("- "):
            listed.append(stripped[2:].strip().strip("\"'"))
            continue
        if in_list and stripped and not stripped.startswith("-"):
            in_list = False
    return listed


def load_sites(package, types):
    name = short_name(package)
    needle = f"omp-jev-{name}"
    sites = []
    for config in config_files():
        for entry in listed_extensions(config):
            target = (
                (config.parent / entry).resolve()
                if not entry.startswith("/")
                else Path(entry)
            )
            blob = entry
            if target.is_file():
                blob += (
                    "\n" + target.read_text(encoding="utf-8", errors="replace")[:4000]
                )
            if needle not in blob and not any(t in blob for t in types):
                continue
            if config == REPO / ".omp" / "config.yml":
                sites.append("project:.omp/config.yml")
            elif config == HOME / ".omp" / "agent" / "config.yml":
                sites.append("agent:default")
            else:
                sites.append(f"profile:{config.parent.parent.name}")
    link_roots = [REPO / ".omp" / "extensions", REPO / ".omp" / "tools"]
    link_roots.append(HOME / ".omp" / "agent" / "extensions")
    link_roots.extend(HOME.glob(".omp/profiles/*/agent/extensions"))
    for root in link_roots:
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if not path.is_symlink():
                continue
            if needle in os.readlink(path) or needle in str(path.resolve()):
                sites.append(f"symlink:{path}")
    return sorted(set(sites))


def session_files():
    roots = [HOME / ".omp" / "agent" / "sessions"]
    roots.extend(HOME.glob(".omp/profiles/*/agent/sessions"))
    files = []
    for root in roots:
        if root.is_dir():
            files.extend(root.rglob("*.jsonl"))
    return roots, files


def session_cwd(path):
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    with fh:
        for i, line in enumerate(fh):
            if i > 40:
                break
            if '"cwd"' not in line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("type") == "session":
                return str(row.get("cwd") or "")
    return ""


def session_location(path):
    """(profile, parts below the sessions root) for a session file.

    The root is the last `agent/sessions` pair: `~/.omp/agent/sessions` is profile `default`,
    `~/.omp/profiles/<name>/agent/sessions` is `<name>`. The first part below it is the encoded
    project dir. Nothing above the root (HOME) is returned, so HOME never classifies a session.
    """
    parts = Path(path).parts
    for i in range(len(parts) - 2, 0, -1):
        if parts[i] == "sessions" and parts[i - 1] == "agent":
            profile = "default"
            if i >= 4 and parts[i - 3] == "profiles" and parts[i - 4] == ".omp":
                profile = parts[i - 2]
            return profile, parts[i + 1 :]
    return "default", parts[-2:]


def is_probe(path, cwd):
    """A probe or test session, judged on the path below its sessions root and the recorded cwd.

    Never on the absolute path: a HOME under /tmp (Linux CI tempdirs) would make every session a
    probe (jev-xpk1 reopen, CI run 36079745187).
    """
    profile, below = session_location(path)
    blob = ("/" + "/".join(below) + "\n" + cwd).lower()
    markers = (
        "/tmp/",
        "/private/tmp/",
        "review-l3",
        "/probe",
        "probe-session",
        "fixture",
    )
    if any(m in blob for m in markers):
        return True
    # The file's own directory: the encoded project dir for a session, the session dir for a
    # subagent file. Always below the root, so never HOME.
    encoded = below[-2].lower() if len(below) > 1 else ""
    if any(m in encoded for m in ("tmp", "probe", "fixture", "review-l3")):
        return True
    if "/test/" in cwd or "/tests/" in cwd or cwd.rstrip("/").endswith("/test"):
        return True
    return profile == "omp-test" or profile.startswith("jev-scratch")


def kind_of(data):
    return str(data.get("kind") or data.get("status") or data.get("outcome") or "")


def bucket(kind):
    if kind.endswith("_error") or kind == "error":
        return "error"
    if "_scored" in kind or kind.endswith("scored"):
        return "scored"
    return "other"


def is_credit(data, timestamp):
    if not timestamp or timestamp < CREDITS_AFTER:
        return False
    blob = json.dumps(data)
    return "402" in blob


def profile_of(path):
    return session_location(path)[0]


def judge_rows(files):
    """(profile, project, probe, row) for each model_usage row whose provider is typesafe."""
    for path in files:
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        where = None
        with fh:
            for line in fh:
                if '"model_usage"' not in line or f'"{JUDGE_PROVIDER}"' not in line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict) or row.get("type") != "model_usage":
                    continue
                if row.get("provider") != JUDGE_PROVIDER:
                    continue
                if where is None:
                    cwd = session_cwd(path)
                    project = Path(cwd).name if cwd else path.parent.name
                    where = (profile_of(path), project or "-", is_probe(path, cwd))
                yield where + (row,)


def usage_of(row):
    usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
    cost = usage.get("cost") if isinstance(usage.get("cost"), dict) else {}
    return int(usage.get("input") or 0), float(cost.get("total") or 0.0)


def is_failure(row):
    return row.get("stopReason") != "stop"


def failure_reason(row):
    text = str(row.get("errorMessage") or row.get("stopReason") or "no stopReason")
    return " ".join(text.split())[:160]


def parse_time(timestamp):
    try:
        return datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
    except ValueError:
        return None


def judge_report(rows):
    """Lines for the judge-role section: calls by kind, day, purpose, profile and project."""
    groups = {}
    failures = {"real": [], "probe": []}
    for profile, project, probe, row in rows:
        kind = "probe" if probe else "real"
        timestamp = str(row.get("timestamp") or "")
        purpose = str(row.get("purpose") or "-")
        key = (kind, timestamp[:10] or "-", purpose, profile, project)
        slot = groups.setdefault(
            key, {"calls": 0, "input": 0, "cost": 0.0, "stops": Counter()}
        )
        tokens, cost = usage_of(row)
        slot["calls"] += 1
        slot["input"] += tokens
        slot["cost"] += cost
        slot["stops"][str(row.get("stopReason") or "-")] += 1
        if is_failure(row):
            failures[kind].append(
                (timestamp, purpose, profile, project, failure_reason(row))
            )
    lines = [
        "# judge role: provider typesafe model_usage rows, one per judge request, failures included",
        "kind\tday\tpurpose\tprofile\tproject\tcalls\tinput_tokens\tcost_usd\tstop_reasons",
    ]
    totals = {"real": [0, 0.0], "probe": [0, 0.0]}
    for key in sorted(groups):
        slot = groups[key]
        totals[key[0]][0] += slot["calls"]
        totals[key[0]][1] += slot["cost"]
        stops = ",".join(f"{k}={v}" for k, v in sorted(slot["stops"].items()))
        lines.append(
            "\t".join(
                list(key)
                + [str(slot["calls"]), str(slot["input"]), f"{slot['cost']:.6f}", stops]
            )
        )
    for kind in ("real", "probe"):
        calls, cost = totals[kind]
        lines.append(
            f"# judge {kind} calls {calls} cost ${cost:.6f} failures {len(failures[kind])}"
        )
    if failures["real"]:
        timestamp, purpose, profile, project, reason = max(failures["real"])
        lines.append(
            f"# last real failure {timestamp} {purpose} {profile}/{project}: {reason}"
        )
    return lines


def fleet_line(rows, now, have_sessions):
    """'Jev judge 24h: N calls, $X, F failures', real sessions only, plus the last failure."""
    if not have_sessions:
        return f"Jev judge 24h: NOT_RUN no omp session files under {SESSION_ROOTS}"
    since = now - timedelta(hours=24)
    calls, cost, failures = 0, 0.0, []
    for profile, _project, probe, row in rows:
        when = parse_time(row.get("timestamp"))
        if probe or when is None or when < since or when > now:
            continue
        calls += 1
        cost += usage_of(row)[1]
        if is_failure(row):
            failures.append(
                (when, str(row.get("purpose") or "-"), profile, failure_reason(row))
            )
    line = f"Jev judge 24h: {calls} calls, ${cost:.4f}, {len(failures)} failures"
    if failures:
        when, purpose, profile, reason = max(failures)
        line += (
            f"; last {when.strftime('%Y-%m-%dT%H:%MZ')} {purpose} {profile}: {reason}"
        )
    return line


def skill_names(row):
    """(tool call id or None, skill name) for each skill one session row reads.

    See the module docstring for the counted shapes. A skill-prompt row has no tool call id.
    """
    if row.get("type") == "custom_message":
        if row.get("customType") != "skill-prompt":
            return []
        match = SKILL_PROMPT_RE.match(str(row.get("content") or ""))
        return [(None, match.group(1))] if match else []
    message = row.get("message")
    if (
        row.get("type") != "message"
        or not isinstance(message, dict)
        or message.get("role") != "assistant"
        or not isinstance(message.get("content"), list)
    ):
        return []
    names = []
    for item in message["content"]:
        if not isinstance(item, dict) or item.get("type") != "toolCall":
            continue
        args = item.get("arguments") if isinstance(item.get("arguments"), dict) else {}
        if item.get("name") == "read":
            name = skill_of_path(str(args.get("path") or ""))
            if name:
                names.append((item.get("id"), name))
        elif item.get("name") == "bash":
            command = str(args.get("command") or "")
            names.extend((item.get("id"), n) for n in sorted(bash_skills(command)))
        elif item.get("name") == "eval":
            code, language = str(args.get("code") or ""), args.get("language")
            names.extend(
                (item.get("id"), n) for n in sorted(code_skills(code, language))
            )
    return names


def skill_reads(files):
    """(session file, probe, timestamp, skill name) for each skill read, one pass per file.

    A tool call whose toolResult came back `isError: true` read nothing and is dropped: a pane
    started before a skill was installed answers `read skill://<name>` with "Unknown skill".
    """
    for path in files:
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        pending, failed = [], set()
        with fh:
            for line in fh:
                error = '"isError":true' in line and '"toolResult"' in line
                skill = ('"toolCall"' in line or '"skill-prompt"' in line) and (
                    "skill://" in line or "/skills/" in line or "skill-prompt" in line
                )
                if not (error or skill):
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                message = row.get("message")
                if isinstance(message, dict) and message.get("role") == "toolResult":
                    if message.get("isError") is True:
                        failed.add(message.get("toolCallId"))
                    continue
                for call_id, name in skill_names(row):
                    pending.append((call_id, row.get("timestamp"), name))
        if not pending:
            continue
        probe = is_probe(path, session_cwd(path))
        for call_id, timestamp, name in pending:
            if call_id is None or call_id not in failed:
                yield path, probe, timestamp, name


def third_party(ledger):
    """Skill names in the ledger's first column, header skipped; None when absent or empty."""
    try:
        text = Path(ledger).read_text(encoding="utf-8")
    except OSError:
        return None
    names = [line.split("\t", 1)[0].strip() for line in text.splitlines()[1:]]
    return list(dict.fromkeys(n for n in names if n)) or None


def skills_line(reads, now, have_sessions, ledger):
    """'Skills 24h: T skill reads in S sessions; third-party k/N read (top: ...); never read N-k'."""
    if not have_sessions:
        return f"Skills 24h: NOT_RUN no omp session files under {SESSION_ROOTS}"
    since = now - timedelta(hours=24)
    counts, sessions = Counter(), set()
    for path, probe, timestamp, name in reads:
        when = parse_time(timestamp)
        if probe or when is None or when < since or when > now:
            continue
        counts[name] += 1
        sessions.add(path)
    line = (
        f"Skills 24h: {sum(counts.values())} skill reads in {len(sessions)} sessions; "
    )
    listed = third_party(ledger)
    if listed is None:
        return line + "third-party NOT_RUN (no ledger)"
    read = sorted((n for n in listed if counts[n]), key=lambda n: (-counts[n], n))
    line += f"third-party {len(read)}/{len(listed)} read"
    if read:
        line += " (top: " + ", ".join(f"{n} x{counts[n]}" for n in read[:3]) + ")"
    return line + f"; never read {len(listed) - len(read)}"


def yaml_scalar(text, number):
    """One secrets.yml value: double-quoted (JSON escapes), single-quoted, or plain.

    Errors name the line number only: a `type: plain` value is itself a secret.
    """
    if text.startswith('"'):
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"line {number}: bad double-quoted value") from None
        return value if isinstance(value, str) else str(value)
    if text.startswith("'"):
        if len(text) < 2 or not text.endswith("'"):
            raise ValueError(f"line {number}: bad single-quoted value")
        return text[1:-1].replace("''", "'")
    return text


def secret_patterns(path):
    """Compiled bytes regexes of the `type: regex` entries of a secrets.yml.

    The omp://secrets.md shape: a list of flat mappings; `flags` or a `/pattern/flags` literal
    (i, m, s honoured). Raises OSError or ValueError; no message quotes a value. An entry that
    does not compile is an error here, where omp would skip it: a census that silently drops
    its only pattern would print 0.
    """
    entries = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for number, raw in enumerate(lines, 1):
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        if text == "-" or text.startswith("- "):
            entries.append({})
            text = text[1:].strip()
            if not text:
                continue
        key, colon, value = text.partition(":")
        if not entries or not colon or not key.strip().isidentifier():
            raise ValueError(f"line {number} is not a `key: value` entry of a list")
        entries[-1][key.strip()] = yaml_scalar(value.strip(), number)
    patterns = []
    for index, entry in enumerate(entries, 1):
        if entry.get("type") != "regex" or not entry.get("content"):
            continue
        source, flags = entry["content"], entry.get("flags", "")
        literal = REGEX_LITERAL.match(source)
        if literal:
            source, flags = literal.groups()
        bits = 0
        for flag in flags:
            bits |= REGEX_FLAGS.get(flag, 0)
        try:
            patterns.append(re.compile(source.encode(), bits))
        except re.error as err:
            raise ValueError(f"entry {index} does not compile ({err.msg})") from None
    if not patterns:
        raise ValueError("no `type: regex` entry")
    return patterns


def is_marked(match):
    """A match whose segment after the first `_` starts with FAKE_MARKER: a fake of ours."""
    parts = match.split(b"_", 2)
    return len(parts) > 1 and parts[1].lower().startswith(FAKE_MARKER)


def key_kind(path, patterns):
    """ "unmarked" at the first unmarked match, else "marked" if any match, else None.

    Streams bytes line by line and reads every match on a line, so a marked fake ahead of a
    real key never hides it. Never returns the matched text."""
    marked = False
    with path.open("rb") as fh:
        for line in fh:
            for pattern in patterns:
                for match in pattern.finditer(line):
                    if not is_marked(match.group()):
                        return "unmarked"
                    marked = True
    return "marked" if marked else None


def key_exposure_line(files, now, have_sessions, secrets):
    """'Key exposure 24h: N session files hold an unmarked TypeSafe-shaped key (S scanned; M hold
    only marked fakes); newest: ...'.

    Every session file modified in the last 24h, probe sessions included (a key printed in a
    probe is on disk all the same). M counts files whose every match carries FAKE_MARKER; they
    are not in N and not named. Unmarked fakes from before the marker (2026-09-25) stay in N until
    their files age out of the 24h window. The newest KEY_NEWEST of the N paths with their
    mtimes; never the matched text.
    """
    head = "Key exposure 24h:"
    try:
        patterns = secret_patterns(secrets)
    except (OSError, ValueError) as err:
        why = err.strerror if isinstance(err, OSError) else str(err)
        return f"{head} NOT_RUN {secrets}: {why}"
    if not have_sessions:
        return f"{head} NOT_RUN no omp session files under {SESSION_ROOTS}"
    cutoff = now.timestamp() - 24 * 3600
    exposed, scanned, marked, unreadable = [], 0, 0, 0
    for path in files:
        try:
            mtime = path.stat().st_mtime
            kind = key_kind(path, patterns) if mtime >= cutoff else None
        except OSError:
            unreadable += 1
            continue
        if mtime < cutoff:
            continue
        scanned += 1
        if kind == "unmarked":
            exposed.append((mtime, str(path)))
        elif kind == "marked":
            marked += 1
    note = f"; {unreadable} unreadable" if unreadable else ""
    line = (
        f"{head} {len(exposed)} session files hold an unmarked TypeSafe-shaped key "
        f"({scanned} scanned; {marked} hold only marked fakes{note})"
    )
    if not exposed:
        return line
    newest = sorted(exposed, reverse=True)[:KEY_NEWEST]
    return (
        line
        + "; newest: "
        + ", ".join(
            f"{path} ({datetime.fromtimestamp(mtime, timezone.utc).strftime('%H:%M')}Z)"
            for mtime, path in newest
        )
    )


def surfaces(roots, files):
    pkgs = packages()
    types_by = {p: decision_types(p) for p in pkgs}
    type_owner = {}
    for package, types in types_by.items():
        for token in types:
            type_owner[token] = package
    tallies = {
        p: {
            "real": 0,
            "probe": 0,
            "error": 0,
            "scored": 0,
            "other": 0,
            "last_scored": "",
            "credits": 0,
        }
        for p in pkgs
    }
    for path in files:
        cwd = session_cwd(path)
        probe = is_probe(path, cwd)
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if "omp-jev-" not in line and "jev-screen.screen.v1" not in line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                token = row.get("customType")
                if not isinstance(token, str) or token not in type_owner:
                    continue
                package = type_owner[token]
                slot = tallies[package]
                if probe:
                    slot["probe"] += 1
                    continue
                slot["real"] += 1
                data = row.get("data") if isinstance(row.get("data"), dict) else {}
                which = bucket(kind_of(data))
                slot[which] += 1
                timestamp = str(row.get("timestamp") or data.get("timestamp") or "")
                if which == "scored" and timestamp > slot["last_scored"]:
                    slot["last_scored"] = timestamp
                if which == "error" and is_credit(data, timestamp):
                    slot["credits"] += 1
    print(
        "package\tloaded\twhere\ttypes\treal_rows\treal_error\treal_scored\treal_other\tlast_scored\tprobe_rows\tcredits_402"
    )
    credits = 0
    for package in pkgs:
        slot = tallies[package]
        sites = load_sites(package, types_by[package])
        credits += slot["credits"]
        print(
            "\t".join(
                [
                    package,
                    "yes" if sites else "no",
                    ",".join(sites) or "-",
                    ",".join(types_by[package]) or "-",
                    str(slot["real"]),
                    str(slot["error"]),
                    str(slot["scored"]),
                    str(slot["other"]),
                    slot["last_scored"] or "-",
                    str(slot["probe"]),
                    str(slot["credits"]),
                ]
            )
        )
    print(
        f"# packages {len(pkgs)} session_files {len(files)} roots {len([r for r in roots if r.is_dir()])} "
        f"credits_402_since_{CREDITS_AFTER} {credits}"
    )


def main(argv):
    roots, files = session_files()
    if "--fleet-line" in argv:
        now = datetime.now(timezone.utc)
        # Session files are append-only, so one untouched for 24h holds no row from the last 24h.
        cutoff = now.timestamp() - 24 * 3600
        recent = []
        for path in files:
            try:
                if path.stat().st_mtime >= cutoff:
                    recent.append(path)
            except OSError:
                continue
        print(fleet_line(judge_rows(recent), now, bool(files)))
        print(skills_line(skill_reads(recent), now, bool(files), SKILL_LEDGER))
        print(key_exposure_line(files, now, bool(files), SECRETS))
        return 0
    if "--judge" not in argv:
        surfaces(roots, files)
    for line in judge_report(judge_rows(files)):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
