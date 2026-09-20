# Six defects in `hyperspaceai/jevcache` — one filed, five drafted, one retraction

Receipt and index. Five of the six ship as complete GitHub issue bodies in the `issue-N-*.md`
files beside this one, paste-ready and unedited. **Those five are unposted.**

The sixth — the `state_preview` credential exposure — was filed by Joshua while this document was
being written: [hyperspaceai/jevcache#1](https://github.com/hyperspaceai/jevcache/issues/1),
2026-09-20T03:29:37Z, with a
[follow-up comment](https://github.com/hyperspaceai/jevcache/issues/1#issuecomment-5747337146)
carrying three additional arms measured in this lane. Our dedup probe caught the issue at 03:33Z,
so `issue-1-*.md` is a record of what was filed and shipped, not a second body for the same bug.
Every upstream artifact is authored on Joshua's account and under his name; this lane drafts and
verifies, it does not author.

`hyperspaceai/jevcache` is a distribution repo — `README.md` and `og.png`, no source. We cannot
send a patch, so "fix them" resolves to two things: local containment (landed separately, see
*Containment* below) and reports good enough that the author can fix each in one sitting.

Every claim below was re-run for this document against the binary in the next section. One claim
briefed to this lane as observed is **retracted**; the retraction is filed before the defects, not
after them. A dedup probe against the upstream repo was run before filing and is reproduced in
every issue body.

## Index

| # | Issue body | Reproduction | One-line summary |
|---|---|---|---|
| 1 | [`issue-1-state-preview-plaintext-credentials.md`](issue-1-state-preview-plaintext-credentials.md) — **filed as #1**, file is a record + shipped comment | `work/jevcache-probe/repro-4-state-preview-credentials.sh` | `state_preview` stores raw state; PII is redacted, credentials are not; file is 0644; no opt-out |
| 2 | [`issue-2-id-field-dropped-before-hashing-collision.md`](issue-2-id-field-dropped-before-hashing-collision.md) | `work/jevcache-probe/repro-6-id-field-collision.sh` | any `*_id` field is dropped **before** hashing, so different states collide and get each other's cached answers |
| 3 | [`issue-3-ledger-no-process-isolation.md`](issue-3-ledger-no-process-isolation.md) | `work/jevcache-probe/repro-3-shared-ledger.sh` | one global ledger, no isolation; concurrent writers corrupt it and lose decisions |
| 4 | [`issue-4-serve-port-flag-handling.md`](issue-4-serve-port-flag-handling.md) | `work/jevcache-probe/repro-2-serve-prints-requested-port.sh` | `serve` prints the requested port, not the bound one (`--port 0` → `:0`); `--port abc` silently discarded |
| 5 | [`issue-5-installer-soft-checksum.md`](issue-5-installer-soft-checksum.md) | `work/jevcache-probe/repro-5-installer-soft-checksum.sh` | a failed `.sha256` fetch downgrades to an unverified install, silently |
| 6 | [`issue-6-documented-decide-example-does-not-run.md`](issue-6-documented-decide-example-does-not-run.md) | `work/jevcache-probe/repro-1-inline-schema-rejected.sh` | the documented `/decide` example cannot be run as written |

Ordered by the order we would fix them, not by when we found them. **2 is the most serious thing
in this file** — it is the only one where the tool returns a confidently wrong answer — and it was
found by pulling on a loose thread in 1.

The two port defects are one issue body because they are one flag-parsing surface. The six
reproduction scripts run with **no API key and no network**, against the built-in `mock` backend
and a throwaway `HOME` (repro-5 fetches the installer and then serves a fake release from
`127.0.0.1`; repro-6 additionally accepts a real backend, which is how the wrong-answer half of
issue 2 is demonstrated). Every one was executed for this document and its output is pasted in the
issue body it supports.

## Environment

| | |
|---|---|
| Binary | `jevcache` **0.1.0** (`jevcache version`) |
| Path | `/Users/josh/.local/bin/jevcache`, Mach-O 64-bit executable arm64, 2,366,912 bytes |
| Identity | sha256 `68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5` — **byte-identical** to the published `https://jevcache.sh/bin/jevcache-darwin-arm64` and to its `.sha256` sidecar, both fetched 2026-09-20 |
| Installed | `curl -fsSL jevcache.sh/install \| sh`, 2026-09-19 20:59 local |
| Host | macOS 26.5.2 (build 25F84), Darwin 25.5.0, arm64 (Apple M3 Ultra), APFS |
| Documented example | `https://jevcache.sh/` landing page, fetched 2026-09-20, 30,319 bytes |
| Upstream README | `github.com/hyperspaceai/jevcache` — distribution repo, `README.md` + `og.png`, no source |
| Live backend (where used) | `JEVCACHE_BACKEND=jev`, `typesafe/jev-1.13.0` |

`jevcache --version` is **not** a flag — it prints help. `jevcache version` prints `0.1.0`.

### What `jevcache.sh/install` actually does

Fetched 2026-09-20, sha256 `1da98e8e5be650db09f873b0ab7bcf6f365bbed4921a2952af18fcff911e1ebb`,
51 lines of POSIX `sh`, read in full because Joshua ran it on this machine.

- **Writes exactly one file.** First of `$HOME/.local/bin`, `/usr/local/bin` that exists and is
  writable, else `$HOME/.local/bin`; `mkdir -p`; downloads `$BASE/bin/jevcache-$os-$arch` to a
  `mktemp` file and `mv`s it in as `jevcache`. Here: `/Users/josh/.local/bin/jevcache`.
- **Touches no shell rc file.** If the dir is not on `PATH` it *prints* a note telling you to
  export it. No `.zshrc`/`.bashrc`/`.profile` edit, no `sudo`, no launch agent, no daemon, no
  uninstall hook.
- **Verifies a checksum, softly** — this is issue 5. Our install *was* verified (sidecar HTTP 200,
  binary matches).
- **Phones home once.** Line 45: `curl -fsS -m3 "$BASE/api/event/install" >/dev/null 2>&1 || true`,
  commented as an "anonymous install counter (best-effort, no data collected beyond a bump)". A
  bare GET, no payload, 3s timeout, failure ignored. Nothing else in the script contacts the
  network beyond the binary and checksum downloads. We read the call; we did not intercept it on
  the wire.

---

## Retracted before filing: "`serve --port 9000` prints port 0"

This lane was briefed that `jevcache serve --port 9000` prints a startup line saying port 0 while
correctly binding 9000. **It does not. The claim is withdrawn and appears in no issue body.**

Provenance, stated plainly because it is the more useful part. The operator reported "jevcache
serve --port 9000 is live on port 0". The conductor checked `lsof`, saw `127.0.0.1:9000 (LISTEN)`,
concluded the bind was fine and therefore the *startup line* must be wrong — and briefed that as
observed. No startup line saying 0 was ever read. That is citing a number without opening its
control, inside a lane whose whole job is not doing that.

Negative evidence, captured 2026-09-20 on the binary above. Five invocation forms, every one
printing the correct port:

```text
jevcache serve --port 9138                  -> jevcache serving on http://127.0.0.1:9138
jevcache serve --port=9138                  -> jevcache serving on http://127.0.0.1:9138
jevcache serve --host 127.0.0.1 --port 9138 -> jevcache serving on http://127.0.0.1:9138
jevcache serve --host 0.0.0.0   --port 9138 -> jevcache serving on http://0.0.0.0:9138
JEVCACHE_PORT=9138 jevcache serve           -> jevcache serving on http://127.0.0.1:9138
```

And the supervised instance the original report was about, from its own captured log:

```text
starting jevcache serve --port 9000 with JEVCACHE_BACKEND=jev (key length 107)
jevcache serving on http://127.0.0.1:9000
  backend: jev   ·   auth: open (localhost)
```

`strings` on the binary finds exactly one `serving on` template and no `port 0` literal.

Issues 3 and 4 are in that same line of code, found while trying to reproduce this, and are filed
on their own evidence — not as a rescue of the retracted claim.

---

## The six, in one paragraph each

Full environment, reproduction, observed/expected and suggested direction are in the linked issue
bodies. This section exists so the receipt stands alone.

**1 — `state_preview` plaintext credentials (filed as #1).** Every `put` row in `ledger.log`
holds a truncated copy of the submitted state. The redactor is good at PII and blind to secrets:
`email` → `<email>`, phone/card/SSN digit runs → `<phone>` or `<num>` — while `password`,
`api_key`, `authorization: "Bearer …"`, `secret` and `private_key` are written verbatim into a
mode-0644 file, with no flag to disable the field. Two sharp edges: a nested
`Authorization: "Bearer FAKE-TOKEN-0000000000000000"` is stored as `"Bearer FAKE-TOKEN-<num>"` —
masking that looks like it fired while the scheme and prefix leak — and
`{"aws_access_key_id":"AKIAIOSFODNN7EXAMPLE"}` is stored as `{}` because `_id` matched the
volatile-identifier rule, while the identical value under the name `aws` is stored in full. Whether
a secret survives depends on what it is called. This does not contradict the site's privacy claim,
which is about what *leaves* the machine; it is about what comes to rest locally, unasked. Pulling
on the deletion half produced defect 2.

**2 — `*_id` fields are dropped before hashing, so different states collide.** The volatile-field
rule removes a field from the canonical state by name suffix, with no check on whether the value is
decision-relevant, and the canonical state is what gets hashed. Measured against the live backend:
`{"command":"rm -rf --no-preserve-root /"}` scores `noul 0.99` and `{"command":"echo hello"}`
scores `0.01`, so the two states are genuinely different. Rename the field to `command_id` and both
produce fingerprint `9aaa9da807f4cc37…`; decide the benign one first and
`rm -rf --no-preserve-root /` comes back **`0.01` — not destructive — `cached=true`,
`source: jev-1.13.0`**, and `recall`, which never calls a backend, returns the same thing offline.
It is symmetric: decide the destructive one first and `echo hello` comes back `0.99`. Identical
fingerprints on `mock`, so it is the canonicalizer and not the backend; the stored
`state_preview` for the colliding pair is literally `{}`. `*_id` is the ordinary name for the thing
a decision is *about* — `ticket_id`, `target_id`, `document_id` — and the README's own worked
example is a ticket router.

**3 — one global ledger, no per-process isolation.** Default `~/.jevcache/ledger.log`, no
namespace, no lock. Confirmed at 21:14 local, read-only and before any containment: a
`POST /decide` to the supervised `serve` instance appended to `/Users/josh/.jevcache/ledger.log`
(`"fingerprint":"57f8e28b…"` present in that file), the same path a bare `jevcache decide` from any
shell would use. Process B `recall`s a decision only process A made (`rc=0`). `JEVCACHE_DIR` *does*
isolate — a clean `rc=3` miss across two scoped dirs — but it is opt-in env, not a flag, absent
from the landing page, and one row of the README config table. And unlocked concurrent appends
corrupt the log: records interleave into one line (`json.loads` → `Extra data: line 1 column 529`)
and a decision reported as written becomes permanently unrecallable. Three batches, same machine,
same evening, 16 concurrent writers each: **3/5**, **2/20**, **1/20** trials with a malformed line;
**1/80**, **7/320**, **2/320** decisions lost. No rate is claimed — only that it is nonzero, and
that `decide` returned success for every one of them.

**4 — `serve` reports the port it was asked for, not the one it bound.** Two halves of one
flag-parsing surface, filed as one issue. `--port 0` prints
`jevcache serving on http://127.0.0.1:0` while `lsof` shows the process listening on
`127.0.0.1:57653`; `curl http://127.0.0.1:0/health` fails with `curl: (7)` and
`curl http://127.0.0.1:57653/health` returns `{"ok":true}`. `--port 0` is the idiom for CI, test
fixtures and sidecars, and stdout is the only channel the caller has. Separately, `--port abc`
does not error: with `JEVCACHE_PORT=57657` set it binds **57657**, proving fall-through rather
than a parse, and with nothing set it goes to the 9000 default. `--port ''` and a valueless
`--port` behave the same. A typo'd port in a service file starts a healthy-looking server on the
wrong one.

**5 — installer soft checksum.** `want=$(curl -fsSL "$url.sha256" 2>/dev/null …)` compared only
inside `if [ -n "$want" ]`. Demonstrated end to end against a local fake release: with the sidecar
absent (404) the installer printed `installed jevcache → …`, exited **0**, and the installed
"binary" printed `NOT THE REAL JEVCACHE`. With a *wrong* sidecar it correctly aborted
(`checksum mismatch — aborting.`, rc=1). The mismatch path works; the missing path is the hole.
Latent, not an incident: this machine's install verified byte-identical.

**6 — the documented `/decide` example cannot be run as written.** The page posts a `schema`
variable it never defines (zero occurrences of `questions` in 30 KB of HTML), and the obvious
fillings are rejected one requirement per round-trip: `schema.id must be a non-empty string` →
`schema.version must be an integer >= 1 (support.route.v1)` → same for `harm.v1` → same for a
string `"1"` → success only at `{id, version:1, questions:{q:{instructions,type}}}`. Five
rejections. `version` cannot be folded into `id` even though `name.vN` and `name@N` are exactly how
the CLI and README write schema references; the `@` form gets a third distinct message
(`schema.id "failure.argument@1" is invalid — use letters, digits, dot, dash, underscore …`,
captured by the sibling evaluation agent). And the question-object shape is validated nowhere
locally — a bare-string question passes jevcache and fails at the backend as
`{"error":"jev backend: https://api.typesafe.ai/v1/systemone: status code 400"}`, HTTP 502. The
working shape had to be reverse-engineered from a `{"t":"schema",…}` row in the ledger.

---

## Separate, softer, and possibly by design: `serve`'s backend is fixed at startup

**Not filed as an issue.** Reading the backend from the process environment is defensible — it
stops a client choosing where inference goes, which is the right default for a networked instance.
Recorded because the *failure mode* cost us two restarts.

`jevcache serve` resolves `JEVCACHE_BACKEND` once, at startup; a client cannot override it (adding
`"backend":"mock"` to the request body changes nothing). An instance started without it defaults to
`local` → `http://127.0.0.1:8080/v1/decide`, and answers every `/decide`:

```text
{"error":"local backend: http://127.0.0.1:8080/v1/decide: status code 404\nno decision backend
reachable. Point JEVCACHE_LOCAL_URL at your model, set JEVCACHE_BACKEND=jev (with JEV_API_KEY),
or =mock to try it out. (recall/use never need a backend.)"}   [http=502]
```

**This corrects our own earlier note.** `work/jevcache-probe/README.md` quotes only the first line
and calls the message one that "reads like a broken model". The full body names the remediation,
and names it well. What survives is narrower: the first line is a 404 against an address the
operator never configured; the startup banner prints `backend: local` where a reader scanning for
trouble will not look; and the same server answers `/health` with `{"ok":true}` while being unable
to decide anything. The 502 arrives per-request rather than at startup, where the misconfiguration
already exists.

One related doc mismatch, noted for completeness: the README config table says the `jev` backend
reads `TYPESAFE_API_KEY`; the binary reads `JEV_API_KEY`.

If it were changed at all, the smallest version is a startup-time reachability check, or a louder
banner when `serve` starts on the default `local` backend with nothing listening at
`JEVCACHE_LOCAL_URL`.

## Containment (local, ours, not a fix)

Defects 1 and 3 were contained on this machine at 21:16 local by the conductor, after the
measurements above and independently of this receipt: `umask 077` in the launcher so ledger files
are born 0600, `JEVCACHE_DIR` pointed at a gitignored mode-0700 directory instead of the shared
`~/.jevcache`, and the old `~/.jevcache` tightened. **The upstream defects stand.** Containment
changes what our machine exposes, not what the tool does, and every measurement in this document
predates it.

## No-claim

- **One machine, one binary version, one evening.** macOS 26.5.2 / arm64, `jevcache 0.1.0`, sha256
  `68fcb95b…`. Nothing here establishes behaviour on Linux, on x64, on another filesystem, or in
  any other version. What one machine and one binary cannot establish, specifically: whether
  defect 3's corruption rate is characteristic or an artifact of APFS and this CPU; whether the
  redactor and canonicalizer rule sets behind defects 1 and 2 are the same on other builds;
  whether any of these are already fixed in an unreleased revision. Defect 3's rate is a race —
  the three batches disagree with each other on purpose. Only "nonzero" is claimed.
- **Defect 2's rule is inferred from behaviour, not read.** We observed that a field named
  `command_id`, `target_id` or `aws_access_key_id` is dropped and that `command`, `target` and
  `aws` are not. We did **not** establish the actual predicate — whether it is a `_id` suffix, a
  substring, a fixed list, or something value-sensitive we did not trip. The collision and the
  wrong cached answer are measured; the rule that causes them is a hypothesis consistent with
  eight observations.
- **We did not read the source.** The upstream repo ships a binary and a README. Every statement
  about internals is inferred from observed behaviour, from `strings`, and from the ledger format.
  No line numbers are cited because there is no code to cite — which also means none of these
  reports can say *where* the bug is, only what it does.
- **Defect 6's ladder is not exhaustive.** We tried the shapes a reader plausibly writes. There may
  be an accepted shape we did not try that the page intended.
- **The reproductions use `JEVCACHE_BACKEND=mock`.** That is what makes them free, offline and
  deterministic; they exercise jevcache's validation, port handling, redactor and ledger, not any
  model's behaviour. Live-backend observations used `typesafe/jev-1.13.0` on 2026-09-20.
- **Every credential in defects 1 and 2 is fake**, typed for the probe, and written to carry an
  explicit `FAKE`/`EXAMPLE` marker or to be a vendor's own published example value. No real
  credential was written to any ledger, and no credential value appears in this receipt or in any
  issue body. The rule exists because a synthetic string shaped like a live key is unreadable as
  fake to a scanner or a maintainer.
- **Not tested at all:** `publish`, `publish --remote`, `add`, `use`, the hosted index at
  `jevcache.sh/api`, `replay`, `market`/`usage`/`earnings`/`wallet`, `JEVCACHE_SERVE_TOKEN`, the
  Docker path, and whether anything is transmitted without an explicit `publish`.
- **Adjacent findings belong to a sibling receipt.** The evaluation agent working the same binary
  found the backend identity absent from the cache key (a `mock` run poisoning a real cache) and
  the model version absent from the default key. Those are in `jevcache-20260919.md` with their own
  captured output and are not re-asserted here. They are the same *class* as defect 2 — things that
  should be in the key and are not, versus something in the key that should not have been removed —
  but they are separate findings with separate evidence, and this file does not merge them.
- **Posting status.** `hyperspaceai/jevcache#1` and its follow-up comment were posted by Joshua,
  on his account, at 2026-09-20T03:29:37Z and shortly after. The five remaining issue bodies in
  this directory are **unposted**. No agent in this lane posted anything. The dedup probe
  reproduced in every issue body was run at 03:33Z — it is a snapshot, and another issue could be
  opened between that timestamp and whenever a human pastes, so re-run it before filing.
