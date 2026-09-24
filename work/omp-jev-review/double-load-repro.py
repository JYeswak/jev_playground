"""Keyless repro: does omp load one extension twice when it is discovered through a project
symlink and also passed with -e by its real path? omp://extension-loading.md says de-duplication
is by absolute path, first seen wins. No model call: rpc session, get_state only."""

import os
import subprocess
import tempfile

T = tempfile.mkdtemp(prefix="dblload.")
real = os.path.join(T, "real", "ext")
proj = os.path.join(T, "proj")
os.makedirs(real)
os.makedirs(os.path.join(proj, ".omp", "extensions"))
with open(os.path.join(real, "index.ts"), "w") as fh:
    fh.write(
        'import { appendFileSync } from "node:fs";\n'
        "export default function (_pi: unknown) {\n"
        '  appendFileSync(process.env.DBL_LOG as string, "loaded\\n");\n'
        "}\n"
    )
os.symlink(real, os.path.join(proj, ".omp", "extensions", "dbl"))
frames = '{"id":"p","type":"negotiate_protocol","protocolVersion":2}\n{"id":"s","type":"get_state"}\n'


def run(tag, *extra):
    log = os.path.join(T, f"{tag}.log")
    env = dict(os.environ, DBL_LOG=log)
    subprocess.run(
        ["omp", "--mode=rpc", "--max-time=15", *extra],
        cwd=proj,
        input=frames,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    n = len(open(log).read().splitlines()) if os.path.exists(log) else 0
    print(f"{tag}: loaded {n} time(s)")


run("symlink-only")
run("symlink-plus-e-real", "-e", os.path.join(real, "index.ts"))
run(
    "symlink-plus-e-symlink",
    "-e",
    os.path.join(proj, ".omp", "extensions", "dbl", "index.ts"),
)
print("tmp", T)
