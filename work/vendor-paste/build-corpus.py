"""vendor-paste corpus v2: file-window labels from committed manifest provenance (keyless)."""

import os, json, re, random, hashlib

REPO = "/Users/josh/Developer/jev"
VENDOR_ROOTS = ("upstream", "docs-mirror")
OWN_ROOTS = ("kit", "scripts", "foundation", ".omp")
SEED = 20261002
PER_FILE = 2
WIN = 60

LIC = re.compile(
    r"Copyright|©|MIT License|Apache License|SPDX-License-Identifier|Licensed under|All rights reserved",
    re.I,
)
TEXT_EXT = (
    ".md",
    ".py",
    ".js",
    ".mjs",
    ".ts",
    ".rs",
    ".go",
    ".sh",
    ".yml",
    ".json",
    ".txt",
    ".toml",
)


def own_walk_ok(root, dirpath):
    parts = dirpath.split(os.sep)
    if "node_modules" in parts or ".venv" in parts:
        return False
    if root == "work":
        low = dirpath.lower()
        if "fork" in low or "/sdk/" in low or "p2-compaction" in low:
            return False
    return True


def windows(root, label, src):
    out = []
    base = os.path.join(REPO, root)
    for dirpath, _, filenames in os.walk(base):
        if label == "neg" and not own_walk_ok(root, dirpath):
            continue
        for fn in sorted(filenames):
            if not fn.endswith(TEXT_EXT):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(fp) > 300000:
                    continue
                with open(fp, encoding="utf-8") as fh:
                    lines = fh.read().split("\n")
            except (OSError, ValueError):
                continue
            if len(lines) < 8:
                continue
            step = max(1, len(lines) // PER_FILE)
            for k in range(PER_FILE):
                s = min(k * step, max(0, len(lines) - WIN))
                w = "\n".join(lines[s : s + WIN])
                if len([l for l in w.split("\n") if l.strip()]) >= 8:
                    out.append(
                        {
                            "file": os.path.relpath(fp, REPO),
                            "src": src,
                            "window": w[:4000],
                            "label": label,
                        }
                    )
    return out


pos, neg = [], []
for root in VENDOR_ROOTS:
    pos.extend(windows(root, "pos", root))
for root in OWN_ROOTS:
    neg.extend(windows(root, "neg", root))
work = windows("work", "neg", "work")
rnd = random.Random(SEED)
rnd.shuffle(work)
neg.extend(work[:1500])
print("pos-windows=%d neg-windows=%d" % (len(pos), len(neg)), flush=True)

for r in pos + neg:
    r["lic"] = bool(LIC.search(r["window"]))
print(
    "pos lic-rate=%.3f neg lic-rate=%.3f"
    % (
        sum(1 for r in pos if r["lic"]) / max(1, len(pos)),
        sum(1 for r in neg if r["lic"]) / max(1, len(neg)),
    ),
    flush=True,
)


def top(r):
    parts = r["file"].split("/")
    return parts[0] + ":" + (parts[1] if len(parts) > 1 else "")


psrc = sorted(set(top(r) for r in pos))
nsrc = sorted(set(top(r) for r in neg))
rnd.shuffle(psrc)
rnd.shuffle(nsrc)
dev_ps, held_ps = set(psrc[: len(psrc) // 2]), set(psrc[len(psrc) // 2 :])
dev_ns, held_ns = set(nsrc[: len(nsrc) // 2]), set(nsrc[len(nsrc) // 2 :])
dev = [
    dict(r, split="dev")
    for r in pos + neg
    if (r["label"] == "pos" and top(r) in dev_ps)
    or (r["label"] == "neg" and top(r) in dev_ns)
]
held = [
    dict(r, split="held")
    for r in pos + neg
    if (r["label"] == "pos" and top(r) in held_ps)
    or (r["label"] == "neg" and top(r) in held_ns)
]
print(
    "dev=%d (pos %d) held=%d (pos %d)"
    % (
        len(dev),
        sum(1 for r in dev if r["label"] == "pos"),
        len(held),
        sum(1 for r in held if r["label"] == "pos"),
    ),
    flush=True,
)

out = dev + held
for i, r in enumerate(out):
    r["row_id"] = "v%04d" % i
    r["win_sha"] = hashlib.sha256(r["window"].encode()).hexdigest()[:12]
with open(REPO + "/work/vendor-paste/corpus.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh)
h = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:12]
print("corpus=%d sha=%s" % (len(out), h), flush=True)
