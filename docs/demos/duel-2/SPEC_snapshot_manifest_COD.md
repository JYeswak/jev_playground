# Q99 Specification: Snapshot Manifest

## Decision: preserve paths, remap at read time

Do not rewrite `STATUS.tsv` or the sidecar inside the snapshot. Rewriting bytes changes the artifact being verified and makes a byte-identical claim ambiguous.

Instead:

1. copy each source file to a private snapshot root while preserving its repository-relative path;
2. retain the original path strings in copied STATUS/sidecar bytes;
3. resolve every relative receipt path as `SNAPSHOT_ROOT / original_relative_path` during verification;
4. reject absolute paths, `..` traversal, and paths outside the repository-relative root;
5. report both `source_path` and `snapshot_path` in the manifest.

The verifier therefore checks the original bytes under a path-remapping context, without mutating the evidence object.

## Input set

For a sidecar verification snapshot, capture exactly:

- `docs/demos/STATUS.tsv`;
- `docs/demos/duel-2/runs/receipt-other-reasons.json`;
- every receipt path referenced by a STATUS row whose `receipt_type=other`;
- any additional sidecar evidence paths that the verifier resolves.

The input set is closed before copying. A path appearing after closure is a snapshot-integrity failure, not an invitation to expand the scan silently.

## Manifest schema

```json
{
  "schema": "jev.snapshot-manifest.v1",
  "snapshot_id": "uuid-or-content-id",
  "source_root": "/absolute/repo/path",
  "source_head": "git HEAD sha",
  "captured_at": "UTC",
  "attempt": 1,
  "files": [
    {
      "source_path": "docs/demos/STATUS.tsv",
      "snapshot_path": "files/docs/demos/STATUS.tsv",
      "bytes": 1234,
      "raw_sha256": "full sha256",
      "normalized_sha256": null,
      "source_pre_sha256": "full sha256",
      "source_post_sha256": "full sha256"
    }
  ],
  "manifest_sha256": "sha256 of canonical manifest payload excluding this field"
}
```

For receipts with the established terminal-whitespace normalization, `normalized_sha256` is required and uses the existing STATUS convention. For STATUS and sidecar files, record `normalized_sha256` when the verifier has a defined normalization; otherwise use `null` and rely on raw identity. Never silently substitute a second digest convention.

`source_pre_sha256` and `source_post_sha256` are the capture stability proof. The copied snapshot's `raw_sha256` must equal both when the attempt is stable.

## Capture protocol

1. Resolve and freeze the input path set.
2. Record `source_head` and `captured_at`.
3. Hash every source file and record `source_pre_sha256`.
4. Copy bytes into a private temporary snapshot root using a temporary destination plus atomic rename. Preserve relative paths; create no symlink escapes.
5. Hash each copied file and compare it with its source pre-hash.
6. Re-hash every source file and record `source_post_sha256`.
7. If any source pre/post hash differs, or any copy hash differs, discard the snapshot and classify the attempt unstable.
8. If stable, compute `manifest_sha256` over canonical JSON with the `manifest_sha256` field omitted, then write the manifest atomically inside the snapshot.
9. Run the verifier against `SNAPSHOT_ROOT`, never against the live source paths.

At most two attempts are allowed. The second attempt's stable result is accepted even when the verifier returns a durable RED. A second unstable capture returns `TRANSIENT_UNSTABLE` with both manifests/change sets and no verifier verdict.

## Manifest digest authority

The manifest digest is self-authenticated but not self-trusting:

- the producer computes it over canonical UTF-8 JSON with the digest field absent;
- the verifier recomputes the same canonical payload and compares the field;
- a third party can independently recompute it from the committed manifest;
- the source file hashes, not the manifest hash alone, establish the evidence binding.

The manifest itself must be stored or returned with the receipt that claims verification. A digest printed only in terminal prose is not evidence.

## Third-party re-derivation

A verifier with repository access can:

1. read `source_head` and the committed source files;
2. recompute each source raw and normalized hash;
3. compare them to the manifest's pre/post/copy hashes;
4. recreate the snapshot path mapping;
5. parse copied STATUS and sidecar bytes;
6. resolve every referenced receipt inside the snapshot;
7. recompute `manifest_sha256`;
8. rerun the sidecar verifier and compare the resulting classification.

A verifier without repository access can still validate the manifest's internal copy hashes and rerun against the snapshot archive, but cannot claim that the snapshot matched the live source at capture time. That boundary must be printed.

## Re-examination condition

Re-examine this design when:

- a source path can be added after input-set closure;
- a receipt uses an absolute path or symlink outside the repository root;
- raw and normalized hashes disagree on what identity means;
- two attempts are insufficient to capture a stable pair in normal operation;
- canonical JSON serialization differs across implementations;
- a verifier consumes a path not listed in the manifest;
- a caller treats a failed manifest digest as a verifier RED instead of snapshot invalidity.

Any change must preserve original source paths, bounded attempts, explicit snapshot identity, and the distinction between `TRANSIENT_UNSTABLE`, invalid snapshot, and durable verifier RED.

## Scope

This is a design contract. It does not implement the snapshot wrapper, alter `verify-other-reasons.sh`, or promote the sidecar verifier. It closes the path-remapping, manifest-authority, and third-party-reproduction decisions required before implementation.
