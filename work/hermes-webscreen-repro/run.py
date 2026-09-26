#!/usr/bin/env python3
"""Reproduce hermes-jev-skills@cf9e84c's web-screen scorecard on web results neither party wrote.

The system under test is theirs, imported read-only: ``jevkit.webscreen.screen()``, and their
harness's ``ATTACKS`` list and ``plant()`` (evals/web-screen/run_eval.py) for arm A. The clean data
is ours to find, not to write: real web tool results in this machine's omp session files, taken
before a fixed cutoff. Arm B plants every label=1 row of deepset/prompt-injections (fetched by
fetch_attacks.py) into the same results.

Arms per text unit, as in their run: today (nothing withheld), hermes (Hermes's scan_for_threats,
reference only), local (webscreen.screen(send=False)), jev+local (webscreen.screen()).

    # keyless: harvest, sample, plant, pack every request, no Jev call
    python3 work/hermes-webscreen-repro/run.py --dry
    # live (preregistered in PREREG.md first)
    infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
        python3 work/hermes-webscreen-repro/run.py --live

The provider is pinned to TypeSafe and the model to jev-1.13.0 (their client reads TYPESAFE_MODEL;
its default is jev-latest). Every row records the model id sent and the id the API returned.

Committed output (--rows) holds hashes, indexes, labels, scores, latency, model ids and usage:
never page text, never URLs, never session paths. Raw sample text goes to --raw-dir, outside the
tree (var/ is not tracked).
"""

import argparse
import hashlib
import importlib.util
import os
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SKILLS = ROOT / "hermes-jev-skills"
sys.path.insert(0, str(SKILLS))
from jevkit import client, keystore, privacy, rerank, webscreen  # noqa: E402

SEED = 20260926  # theirs (run_eval.py:41)
PER_KIND = 40  # 40 search-like + 40 page-like = their two samples of 40
CUTOFF = "2026-09-26T00:00:00Z"  # results recorded after this are not in the pool
MODEL = "jev-1.13.0"  # pinned; their client's default id is jev-latest (client.py:24)
ENGINES = {
    "mojeek",
    "duckduckgo",
    "startpage",
    "parallel",
}  # providers that return engine snippets
PAGE_TYPES = ("text/html", "text/markdown", "text/plain")
PARTY = re.compile(r"(?i)jyeswak|zeststream|jev_playground|kerpopule|hermes-jev-skills")
PRIVATE_HOST = re.compile(
    r"(?i)^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|\[::1\])"
)
OMP_TRAILER = re.compile(r"\n+\[Showing lines [^\n]*\]\s*$")
HERMES_AGENT = Path.home() / ".hermes" / "hermes-agent"


def their_harness():
    """run_eval.py imported as a module: ATTACKS and plant() are used exactly as committed."""
    spec = importlib.util.spec_from_file_location(
        "hermes_run_eval", SKILLS / "evals" / "web-screen" / "run_eval.py"
    )
    module = importlib.util.module_from_spec(spec)
    saved = sys.argv
    sys.argv = [saved[0]]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = saved
    return module


def hermes_scan():
    if not (HERMES_AGENT / "tools" / "threat_patterns.py").is_file():
        return None
    sys.path.insert(0, str(HERMES_AGENT))
    from tools.threat_patterns import scan_for_threats  # type: ignore

    return scan_for_threats


def sha(text, n=16):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def credential_shaped(text):
    """Their own redactor finds a secret-shaped run (token shapes, KEY=value, high-entropy mixed)."""
    return "[secret]" in privacy.redact(text, limit=len(text) + 1)


def session_roots():
    home = Path.home()
    return [
        home / ".omp" / "agent" / "sessions",
        *sorted((home / ".omp" / "profiles").glob("*/agent/sessions")),
    ]


def candidate_files(pattern):
    roots = [str(r) for r in session_roots() if r.is_dir()]
    out = subprocess.run(["rg", "-l", pattern, *roots], capture_output=True, text=True)
    if out.returncode not in (0, 1):
        raise SystemExit(f"rg failed: {out.stderr.strip()}")
    return sorted(set(out.stdout.split()))


def entries(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if isinstance(entry, dict) and isinstance(entry.get("message"), dict):
                yield entry, entry["message"]


def text_of(message):
    return "".join(
        part.get("text", "")
        for part in message.get("content") or []
        if isinstance(part, dict)
    )


def source_id(path, call_id):
    return f"{Path(path).relative_to(Path.home())}#{call_id}"


def search_pool():
    """web_search results whose provider returned engine snippets, in their web_search shape."""
    pool = []
    for path in candidate_files('"toolName":"web_search"'):
        for entry, message in entries(path):
            if (
                message.get("role") != "toolResult"
                or message.get("toolName") != "web_search"
            ):
                continue
            if message.get("isError") or entry.get("timestamp", "9") >= CUTOFF:
                continue
            response = (message.get("details") or {}).get("response") or {}
            sources = response.get("sources") or []
            if response.get("provider") not in ENGINES or not sources:
                continue
            web = [
                {
                    "url": s.get("url") or "",
                    "title": s.get("title") or "",
                    "description": s.get("snippet") or "",
                }
                for s in sources
                if isinstance(s, dict)
            ]
            if any(
                PARTY.search(" ".join(w.values())) or PRIVATE_HOST.search(w["url"])
                for w in web
            ):
                continue
            raw = json.dumps({"data": {"web": web}}, indent=2, ensure_ascii=False)
            pool.append(
                {
                    "kind": "search",
                    "tool": "web_search",
                    "source": source_id(path, message.get("toolCallId")),
                    "provider": response.get("provider"),
                    "raw": raw,
                }
            )
    return pool


def page_pool():
    """read results of http(s) URLs, omp's own header and trailer removed, in their web_extract shape."""
    pool = []
    for path in candidate_files(r'"name":"read","arguments":\{[^}]*"path":"https?://'):
        calls = {}
        for entry, message in entries(path):
            if message.get("role") == "assistant":
                for part in message.get("content") or []:
                    if (
                        isinstance(part, dict)
                        and part.get("type") == "toolCall"
                        and part.get("name") == "read"
                    ):
                        target = (part.get("arguments") or {}).get("path")
                        if isinstance(target, str) and re.match(r"https?://", target):
                            calls[part.get("id")] = target
                continue
            if (
                message.get("role") != "toolResult"
                or message.get("toolCallId") not in calls
            ):
                continue
            if message.get("isError") or entry.get("timestamp", "9") >= CUTOFF:
                continue
            details = message.get("details") or {}
            url = (
                details.get("finalUrl")
                or details.get("url")
                or calls[message["toolCallId"]]
            )
            if details.get("kind") != "url" or not str(
                details.get("contentType") or ""
            ).startswith(PAGE_TYPES):
                continue
            if PARTY.search(url) or PRIVATE_HOST.search(url):
                continue
            text = text_of(message)
            if not text.startswith("URL:") or "\n\n---\n\n" not in text:
                continue
            page = OMP_TRAILER.sub("", text.split("\n\n---\n\n", 1)[1])
            if PARTY.search(page):
                continue
            raw = json.dumps(
                {"results": [{"url": url, "content": page}]},
                indent=2,
                ensure_ascii=False,
            )
            pool.append(
                {
                    "kind": "page",
                    "tool": "web_extract",
                    "source": source_id(path, message["toolCallId"]),
                    "provider": details.get("contentType"),
                    "url": url,
                    "raw": raw,
                }
            )
    return pool


def admit(pool):
    """Their filters (length > 400, at least two units, first-300-characters dedupe) plus ours."""
    urls, heads, kept = set(), set(), []
    dropped = {"short": 0, "units": 0, "duplicate": 0, "credential": 0}
    for item in sorted(pool, key=lambda i: i["source"]):
        _, units = webscreen.units(item["tool"], item["raw"])
        body = "\n".join(text for _, text in units)
        if len(body) <= 400:
            dropped["short"] += 1
        elif len(units) < 2:
            dropped["units"] += 1
        elif body[:300] in heads or (item.get("url") and item["url"] in urls):
            dropped["duplicate"] += 1
        elif credential_shaped(item["raw"]):
            dropped["credential"] += 1
        else:
            heads.add(body[:300])
            if item.get("url"):
                urls.add(item["url"])
            kept.append(item)
    return kept, dropped


def load_b(path):
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Recorder:
    """A transport that sends exactly what client.ask built, and keeps model ids and usage."""

    def __init__(self, live):
        self.live = live
        self.calls = []
        self.bodies = []

    def __call__(self, body, headers, timeout):
        sent = json.loads(body)
        record = {
            "model_sent": sent.get("model"),
            "passages": len(sent.get("questions") or {}),
        }
        self.bodies.append(sent)
        if not self.live:
            self.calls.append({**record, "error": "dry_run"})
            raise client.JevError("dry_run")
        try:
            raw = client._http_transport(body, headers, timeout)
        except client.JevError as error:
            self.calls.append({**record, "error": error.code})
            raise
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = {}
        usage = (
            payload.get("usage")
            if isinstance(payload, dict) and isinstance(payload.get("usage"), dict)
            else {}
        )
        self.calls.append(
            {
                **record,
                "model_served": payload.get("model")
                if isinstance(payload, dict)
                else None,
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
            }
        )
        return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument(
        "--attacks-b",
        default=str(ROOT / "var/agent-tmp/hermes-webscreen-repro/attacks-b.jsonl"),
    )
    parser.add_argument(
        "--raw-dir", default=str(ROOT / "var/agent-tmp/hermes-webscreen-repro")
    )
    parser.add_argument(
        "--rows", default=None, help="rows file (default: rows.jsonl here when --live)"
    )
    parser.add_argument("--manifest", default=str(HERE / "sample-manifest.json"))
    args = parser.parse_args()
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    if args.dry:
        # client.ask resolves a key before it calls the transport; the dry transport raises before
        # anything is sent, so a placeholder lets every request be built and measured keylessly.
        os.environ["TYPESAFE_API_KEY"] = "dry-run-placeholder-not-a-key"
        os.environ.pop("TYPESAFE_BASE_URL", None)
    os.environ["JEV_PROVIDER"] = "typesafe"
    os.environ["TYPESAFE_MODEL"] = MODEL
    if args.live and (
        keystore.provider() != "typesafe" or os.environ.get("TYPESAFE_BASE_URL")
    ):
        print("no TypeSafe key resolvable (or a base-URL override is set); aborting")
        return 2

    harness = their_harness()
    scan = hermes_scan()
    attacks_a = [{"id": f"A{i:02d}", "text": t} for i, t in enumerate(harness.ATTACKS)]
    attacks_b = [{"id": a["id"], "text": a["text"]} for a in load_b(args.attacks_b)]

    searches, search_dropped = admit(search_pool())
    pages, page_dropped = admit(page_pool())
    random.seed(SEED)
    random.shuffle(searches)
    random.shuffle(pages)
    results = searches[:PER_KIND] + pages[:PER_KIND]

    screenings = []  # (result index, arm, attack id, text, planted unit indexes)
    for n, item in enumerate(results):
        screenings.append((n, "clean", None, item["raw"], []))
    for n, item in enumerate(results):
        attack = attacks_a[n % len(attacks_a)]
        attacked, hits = harness.plant(item["tool"], item["raw"], attack["text"])
        screenings.append((n, "A", attack["id"], attacked, hits))
    for j, attack in enumerate(attacks_b):
        n = j % len(results)
        attacked, hits = harness.plant(
            results[n]["tool"], results[n]["raw"], attack["text"]
        )
        screenings.append((n, "B", attack["id"], attacked, hits))

    manifest = {
        "seed": SEED,
        "cutoff": CUTOFF,
        "engines": sorted(ENGINES),
        "page_types": list(PAGE_TYPES),
        "pool": {"search": len(searches), "page": len(pages)},
        "dropped": {"search": search_dropped, "page": page_dropped},
        "results": [
            {
                "result": n,
                "kind": r["kind"],
                "tool": r["tool"],
                "provider": r["provider"],
                "source_sha": sha(r["source"]),
                "raw_sha": sha(r["raw"], 64),
                "units": len(webscreen.units(r["tool"], r["raw"])[1]),
            }
            for n, r in enumerate(results)
        ],
        "screenings": len(screenings),
        "planted": {
            arm: sum(len(s[4]) for s in screenings if s[1] == arm) for arm in ("A", "B")
        },
        "plant_missing": {
            arm: sum(1 for s in screenings if s[1] == arm and not s[4])
            for arm in ("A", "B")
        },
    }
    manifest["sample_sha"] = sha("".join(r["raw_sha"] for r in manifest["results"]), 64)
    (raw_dir / "sample.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results)
    )
    if args.live:
        frozen = json.loads(Path(args.manifest).read_text())
        frozen_b = json.loads((HERE / "attacks-b-manifest.json").read_text())
        b_now = [
            hashlib.sha256(a["text"].encode("utf-8")).hexdigest() for a in attacks_b
        ]
        if (
            frozen["sample_sha"] != manifest["sample_sha"]
            or frozen["planted"] != manifest["planted"]
            or b_now != [a["sha256"] for a in frozen_b["attacks"]]
        ):
            print("sample or attacks differ from the preregistered manifests; aborting")
            return 3
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    rows_path = (
        Path(args.rows)
        if args.rows
        else (HERE / "rows.jsonl" if args.live else raw_dir / "rows-dry.jsonl")
    )
    states = []
    with rows_path.open("w", encoding="utf-8") as out:
        for k, (n, arm, attack_id, text, planted) in enumerate(screenings):
            item = results[n]
            _, units = webscreen.units(item["tool"], text)
            recorder = Recorder(args.live)
            started = time.monotonic()
            verdict = webscreen.screen(
                item["tool"], text, send=True, transport=recorder
            )
            elapsed = int((time.monotonic() - started) * 1000)
            local_only = webscreen.screen(item["tool"], text, send=False)
            states += [
                {"id": f"s{k}-{b}", "state": body["state"]}
                for b, body in enumerate(recorder.bodies)
            ]
            row = {
                "screening": k,
                "result": n,
                "kind": item["kind"],
                "tool": item["tool"],
                "source_sha": sha(item["source"]),
                "arm": arm,
                "attack": attack_id,
                "units": len(units),
                "unit_sha": [sha(t) for _, t in units],
                "planted": planted,
                "flagged_jev_local": verdict.get("flagged", []),
                "flagged_local": local_only.get("flagged", []),
                "flagged_hermes": (
                    [i for i, (_, t) in enumerate(units) if scan(t, scope="context")]
                    if scan
                    else None
                ),
                "scores": {str(i): s for i, s in (verdict.get("scores") or {}).items()},
                "judged": verdict.get("judged"),
                "status": verdict.get("status"),
                "screening_mode": verdict.get("screening"),
                "reason": verdict.get("reason"),
                "latency_ms": elapsed,
                "jev_latency_ms": verdict.get("latency_ms"),
                "requests": len(recorder.calls),
                "model_sent": sorted(
                    {c["model_sent"] for c in recorder.calls if c.get("model_sent")}
                ),
                "model_served": sorted(
                    {c["model_served"] for c in recorder.calls if c.get("model_served")}
                ),
                "request_errors": [
                    c["error"] for c in recorder.calls if c.get("error")
                ],
                "input_tokens": sum(c.get("input_tokens") or 0 for c in recorder.calls),
                "output_tokens": sum(
                    c.get("output_tokens") or 0 for c in recorder.calls
                ),
            }
            out.write(json.dumps(row) + "\n")
            out.flush()
    (raw_dir / ("states-live.jsonl" if args.live else "states-dry.jsonl")).write_text(
        "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in states)
    )
    if args.dry:
        question = client.noul(rerank.injection_question("P479"))
        manifest["longest_question_bytes"] = len(
            json.dumps(question, separators=(",", ":")).encode("utf-8")
        )
        manifest["requests_dry"] = len(states)
        Path(args.manifest).write_text(json.dumps(manifest, indent=1) + "\n")
    if args.live:

        def head(path):
            out = subprocess.run(
                ["git", "-C", str(path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
            )
            return out.stdout.strip() or None

        meta = {
            "started_utc": started_utc,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "python": sys.version.split()[0],
            "model_pinned": MODEL,
            "provider": keystore.provider(),
            "jev_head": head(ROOT),
            "hermes_jev_skills_head": head(SKILLS),
            "hermes_agent_head": head(HERMES_AGENT) if scan else None,
            "sample_sha": manifest["sample_sha"],
            "screenings": len(screenings),
            "rows": rows_path.name,
        }
        (HERE / "run-meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "results"}, indent=1))
    print(f"rows -> {rows_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
