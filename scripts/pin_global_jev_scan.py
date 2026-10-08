"""Discover globally loaded Jev surfaces from a committed import graph."""
from __future__ import annotations

import posixpath
from pathlib import Path, PurePosixPath
from typing import Any

from pin_global_jev_common import (
    MAX_CLOSURE_FILES,
    SOURCE_SUFFIXES,
    PinError,
    git_blob,
    sha256,
)


def strip_yaml_comment(line: str) -> str:
    quote = ""
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif quote and char == "\\" and quote == '"':
            escaped = True
        elif quote and char == quote:
            quote = ""
        elif not quote and char in "'\"":
            quote = char
        elif not quote and char == "#":
            return line[:index]
    return line


def scalar_span(line: str, start: int, end: int) -> tuple[str, int, int, str]:
    while start < end and line[start].isspace():
        start += 1
    while end > start and line[end - 1].isspace():
        end -= 1
    if start == end:
        raise PinError("empty extension entry")
    quote = line[start] if line[start] in "'\"" else ""
    value_start = start + 1 if quote else start
    value_end = end - 1 if quote and line[end - 1] == quote else end
    if quote and value_end == end:
        raise PinError("unterminated quoted extension entry")
    return line[value_start:value_end], value_start, value_end, quote


def extension_refs(config: Path, text: str) -> list[dict[str, Any]]:
    lines = text.splitlines(keepends=True)
    refs: list[dict[str, Any]] = []
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    found = False
    index = 0
    while index < len(lines):
        clean = strip_yaml_comment(lines[index].rstrip("\r\n"))
        unindented = clean.lstrip()
        if clean[: len(clean) - len(unindented)] or not unindented.startswith("extensions:"):
            index += 1
            continue
        if found:
            raise PinError(f"multiple top-level extensions lists in {config}")
        found = True
        inline = unindented[len("extensions:") :].strip()
        if inline:
            if inline != "[]":
                raise PinError(f"unsupported inline extensions list in {config}:{index + 1}")
            index += 1
            continue
        index += 1
        while index < len(lines):
            raw = lines[index].rstrip("\r\n")
            clean = strip_yaml_comment(raw)
            if not clean.strip():
                index += 1
                continue
            indent = len(clean) - len(clean.lstrip())
            if indent == 0:
                break
            left = len(clean) - len(clean.lstrip())
            item = clean[left:]
            if not item.startswith("-") or (len(item) > 1 and not item[1].isspace()):
                raise PinError(f"unsupported extensions-list form in {config}:{index + 1}")
            value, value_start, value_end, quote = scalar_span(raw, left + 1, len(clean))
            refs.append({
                "config": config,
                "line": index + 1,
                "value": value,
                "start": offsets[index] + value_start,
                "end": offsets[index] + value_end,
                "quote": quote,
            })
            index += 1
    return refs


def resolve_extension(value: str, config: Path, home: Path, repo: Path) -> Path:
    expanded = value
    if expanded.startswith("~/"):
        expanded = str(home / expanded[2:])
    candidate = Path(expanded)
    if candidate.is_absolute():
        return candidate.resolve(strict=False)
    for base in (repo, config.parent, home):
        resolved = (base / candidate).resolve(strict=False)
        if resolved.exists():
            return resolved
    return (repo / candidate).resolve(strict=False)


def parse_quoted(line: str, start: int) -> tuple[str, int, int] | None:
    while start < len(line) and line[start].isspace():
        start += 1
    if start >= len(line) or line[start] not in "'\"":
        return None
    quote = line[start]
    end = start + 1
    escaped = False
    while end < len(line):
        char = line[end]
        if escaped:
            escaped = False
        elif char == "\\" and quote == '"':
            escaped = True
        elif char == quote:
            return line[start + 1 : end], start + 1, end
        end += 1
    return None


def module_literals(source: str) -> list[tuple[str, int, int]]:
    """Read ordinary one-line ESM import/export specifiers without executing code."""
    found: list[tuple[str, int, int]] = []
    offset = 0
    for line in source.splitlines(keepends=True):
        stripped = line.lstrip()
        if not stripped.startswith(("//", "/*", "*")):
            statement_start = len(line) - len(stripped)
            quote_start: int | None = None
            if stripped.startswith(("import ", "import\t", "export ", "export\t")):
                from_at = stripped.rfind(" from ")
                if from_at >= 0:
                    quote_start = statement_start + from_at + len(" from ")
                elif stripped.startswith("import "):
                    quote_start = statement_start + len("import ")
                if quote_start is not None:
                    parsed = parse_quoted(line, quote_start)
                    if parsed:
                        value, begin, end = parsed
                        found.append((value, offset + begin, offset + end))
            search = 0
            while True:
                call = line.find("import(", search)
                if call < 0:
                    break
                parsed = parse_quoted(line, call + len("import("))
                if parsed:
                    value, begin, end = parsed
                    found.append((value, offset + begin, offset + end))
                search = call + len("import(")
        offset += len(line)
    return found


def sdk_path_constants(source: str) -> list[str]:
    values: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith("const ") or "=" not in stripped:
            continue
        name, value = stripped[6:].split("=", 1)
        if name.strip() != "SDK_PATH":
            continue
        parsed = parse_quoted(value, 0)
        if parsed:
            values.append(parsed[0])
    return values


def normalize_repo_target(source_rel: str, specifier: str, repo: Path) -> str | None:
    if specifier.startswith(str(repo) + "/"):
        return posixpath.normpath(specifier[len(str(repo)) + 1 :])
    if specifier.startswith("/"):
        return None
    if not specifier.startswith(("./", "../")):
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_rel), specifier))


def resolve_tree_file(target: str, tree: dict[str, str]) -> str | None:
    target = posixpath.normpath(target)
    candidates = [target]
    if not PurePosixPath(target).suffix:
        candidates.extend(target + suffix for suffix in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts", ".cjs", ".cts"))
        candidates.extend(posixpath.join(target, "index" + suffix) for suffix in (".ts", ".tsx", ".js", ".mjs"))
    for candidate in candidates:
        if candidate in tree:
            return candidate
    return None


def repo_rel(path: Path, repo: Path) -> str | None:
    try:
        return path.resolve(strict=False).relative_to(repo).as_posix()
    except ValueError:
        return None


def config_paths(home: Path) -> list[Path]:
    root = home / ".omp"
    paths = [root / "agent" / "config.yml"]
    profiles = root / "profiles"
    if profiles.is_dir():
        for child in sorted(profiles.iterdir()):
            if child.is_dir():
                paths.append(child / "agent" / "config.yml")
    return [path for path in paths if path.is_file()]


def global_source_dirs(home: Path) -> list[Path]:
    root = home / ".omp"
    dirs = [
        root / "omp-extensions",
        root / "agent" / "hooks" / "pre",
        root / "agent" / "hooks" / "post",
    ]
    profiles = root / "profiles"
    if profiles.is_dir():
        for child in sorted(profiles.iterdir()):
            if child.is_dir():
                agent = child / "agent"
                dirs.extend((agent / "hooks" / "pre", agent / "hooks" / "post"))
    return dirs


def tracked_inode_sources(repo: Path, tree: dict[str, str]) -> dict[tuple[int, int], list[str]]:
    result: dict[tuple[int, int], list[str]] = {}
    for rel in tree:
        if Path(rel).suffix.lower() not in SOURCE_SUFFIXES:
            continue
        path = repo / rel
        try:
            info = path.stat()
        except OSError:
            continue
        result.setdefault((info.st_dev, info.st_ino), []).append(rel)
    return result


def source_path_by_hash(repo: Path, commit: str, tree: dict[str, str], file: Path) -> str | None:
    digest = sha256(file.read_bytes())
    candidates = [rel for rel in tree if Path(rel).name == file.name and Path(rel).suffix.lower() in SOURCE_SUFFIXES]
    for rel in candidates:
        try:
            if sha256(git_blob(repo, commit, rel)) == digest:
                return rel
        except PinError:
            continue
    return None

def discover(repo: Path, home: Path, commit: str, tree: dict[str, str]) -> dict[str, Any]:
    configs: list[dict[str, Any]] = []
    entry_sources: dict[str, set[str]] = {"extension": set(), "hook": set()}
    for config in config_paths(home):
        text = config.read_text(encoding="utf-8")
        refs = extension_refs(config, text)
        rows = []
        for ref in refs:
            target = resolve_extension(ref["value"], config, home, repo)
            rel = repo_rel(target, repo)
            rows.append({"line": ref["line"], "value": ref["value"], "source": rel})
            if rel is not None:
                if rel not in tree:
                    raise PinError(f"globally loaded extension is not in commit {commit}: {rel}")
                entry_sources["extension"].add(rel)
        configs.append({"path": str(config), "entries": rows})

    inode_sources = tracked_inode_sources(repo, tree)
    hooks: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for directory in global_source_dirs(home):
        if not directory.is_dir():
            continue
        for file in sorted(directory.iterdir()):
            if file in seen or file.suffix.lower() not in SOURCE_SUFFIXES or not file.is_file():
                continue
            seen.add(file)
            source_rel: str | None = None
            try:
                info = file.stat()
                linked = inode_sources.get((info.st_dev, info.st_ino), [])
                if linked:
                    source_rel = linked[0]
            except OSError:
                pass
            source_text = file.read_text(encoding="utf-8", errors="strict")
            if source_rel is None:
                for spec, _start, _end in module_literals(source_text):
                    imports_checkout = spec.startswith(str(repo) + "/")
                    if not imports_checkout and spec.startswith(("./", "../")):
                        imports_checkout = (file.parent / spec).resolve(strict=False).is_relative_to(repo)
                    if imports_checkout:
                        source_rel = source_path_by_hash(repo, commit, tree, file)
                        if source_rel is None:
                            raise PinError(f"global hook imports the checkout but has no matching committed source: {file}")
                        break
            if source_rel is None:
                continue
            if source_rel not in tree:
                raise PinError(f"global hook source is not in commit {commit}: {source_rel}")
            entry_sources["hook"].add(source_rel)
            hooks.append({"path": str(file), "source": source_rel, "sha256": sha256(file.read_bytes())})

    closure: set[str] = set()
    external_sdk = False
    pending = list(entry_sources["extension"] | entry_sources["hook"])
    while pending:
        source_rel = pending.pop()
        if source_rel in closure:
            continue
        if len(closure) >= MAX_CLOSURE_FILES:
            raise PinError(f"import closure exceeds {MAX_CLOSURE_FILES} files")
        if source_rel not in tree:
            raise PinError(f"import is not present in committed tree: {source_rel}")
        closure.add(source_rel)
        source = git_blob(repo, commit, source_rel).decode("utf-8")
        for spec, _start, _end in module_literals(source):
            target = normalize_repo_target(source_rel, spec, repo)
            if target is None:
                continue
            resolved = resolve_tree_file(target, tree)
            if resolved is not None:
                pending.append(resolved)
            elif target.startswith("work/sdk/node_modules/@typesafe-ai/sdk/"):
                external_sdk = True
            elif "node_modules" not in PurePosixPath(target).parts:
                raise PinError(f"unresolved local import in {source_rel}: {spec}")
        for spec in sdk_path_constants(source):
            target = normalize_repo_target(source_rel, spec, repo)
            if target and target.startswith("work/sdk/node_modules/@typesafe-ai/sdk/"):
                external_sdk = True
    closure_details = []
    for rel in sorted(closure):
        data = git_blob(repo, commit, rel)
        closure_details.append({"path": rel, "source_sha256": sha256(data), "bytes": len(data)})
    return {
        "commit": commit,
        "configs": configs,
        "hooks": hooks,
        "entrypoints": {
            "extensions": sorted(entry_sources["extension"]),
            "hooks": sorted(entry_sources["hook"]),
        },
        "closure": sorted(closure),
        "closure_details": closure_details,
        "external_sdk": external_sdk,
    }
