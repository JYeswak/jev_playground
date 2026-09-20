# Issue 1 — FILED AND ANSWERED UPSTREAM. Nothing here is pending.

**Issue:** [hyperspaceai/jevcache#1](https://github.com/hyperspaceai/jevcache/issues/1) —
"state_preview persists unredacted credentials to a world-readable ledger"
· filed by **Joshua** · 2026-09-20T03:29:37Z · state OPEN

**Follow-up comment:**
[issue #1, comment 5747337146](https://github.com/hyperspaceai/jevcache/issues/1#issuecomment-5747337146)
· posted by Joshua · carries the three additional arms measured in this lane

Every upstream artifact in this repo is authored on Joshua's account and under his name. This
file is a record of what was filed and what was added to it — it is not an issue body to post,
and nothing in it is outstanding.

### How this file came to be a record instead of a draft

A body for this defect was drafted here. The dedup probe run before filing — jeff-issue-chain
Phase −1 — found the issue already open, four minutes old:

```sh
$ gh issue list --repo hyperspaceai/jevcache --state all --limit 30
1  OPEN  state_preview persists unredacted credentials to a world-readable ledger  2026-09-20T03:29:37Z

$ gh release list --repo hyperspaceai/jevcache --limit 5
jevcache v0.1.0  Latest  v0.1.0  2026-09-19T17:44:40Z
```

`v0.1.0` is the only release, so the behaviour is not fixed in a newer tag. The draft was
discarded rather than filed as a duplicate, and the part of it that was genuinely new — three
measured arms the filed issue did not contain — became the follow-up comment.

### The three arms, as shipped

All measured on `jevcache 0.1.0`, sha256
`68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5`, macOS 26.5.2 arm64,
`JEVCACHE_BACKEND=mock`, throwaway `HOME`, every credential value fake. Reproduction script:
`work/jevcache-probe/repro-4-state-preview-credentials.sh`. Each was independently re-run
before the comment was posted.

**Arm 1 — the class enumerated.** Five credential field names, each in its own single-field
state, all stored verbatim in `r.state_preview`:

```text
  password     out : {"password":"hunter2-correct-horse-battery"}
  api_key      out : {"api_key":"sk-live-FAKE-EXAMPLE-NOT-A-REAL-KEY"}
  authorization out: {"authorization":"Bearer FAKE-EXAMPLE-NOT-A-REAL-TOKEN"}
  secret       out : {"secret":"s3cr3t-value-not-a-number"}
  private_key  out : {"private_key":"-----BEGIN RSA PRIVATE KEY-----FAKE-----END RSA PRIVATE KEY-----"}
```

**Arm 2 — a field-name rule silently deletes real content.** The same AWS example key under
two names, opposite outcomes:

```text
  {"aws_access_key_id":"AKIAIOSFODNN7EXAMPLE"}  ->  {}
  {"aws":"AKIAIOSFODNN7EXAMPLE"}                ->  {"aws":"AKIAIOSFODNN7EXAMPLE"}
```

**Arm 3 — the digit rule mangles token-shaped values instead of protecting them**, nested:

```text
  {"headers":{"Authorization":"Bearer FAKE-TOKEN-0000000000000000"}}
       ->  {"headers":{"Authorization":"Bearer FAKE-TOKEN-<num>"}}
```

The mask makes it look like a redaction rule fired. What survives — the scheme and the token's
identifying prefix — is the part that says what the credential is and who issued it. The
original measurement, before the fake-credential-shape rule below was adopted, used a longer
40-digit run and produced `<phone>` rather than `<num>`, so the masker has at least two digit
classes; neither protects the value.

### What arm 2 turned into

Arm 2's deletion half is **not a privacy defect at all**, and that is the more valuable read:
a rule intended for volatile ids is dropping decision-relevant content *before* hashing, so two
materially different states can collide on one fingerprint. That is a cache-correctness bug
that would matter if nothing secret were ever stored. It is filed separately and with its own
evidence as [`issue-2-id-field-dropped-before-hashing-collision.md`](issue-2-id-field-dropped-before-hashing-collision.md),
where the collision is demonstrated end to end against a live model:
`rm -rf --no-preserve-root /` served `0.01` "not destructive" from cache, because
`echo hello` was decided first under the same `command_id` field name.

### One rule adopted from this exchange

Do not put a string shaped like a live credential into an upstream artifact, even a fake one —
scanners and human readers cannot tell. Use an explicit `FAKE`/`EXAMPLE` marker, or a vendor's
own published example value (`AKIAIOSFODNN7EXAMPLE`). The literal 40-character `ghp_` shape
originally drafted here was replaced for exactly that reason, and the values above and in
`repro-4-*.sh` follow the rule.
