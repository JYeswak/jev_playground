"""Offline tests for the X7 frozen-frame preparation rules."""

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("prepare.py")
SPEC = importlib.util.spec_from_file_location("_x7_prepare", MODULE_PATH) if MODULE_PATH.exists() else None
prepare = importlib.util.module_from_spec(SPEC) if SPEC else None
if SPEC and SPEC.loader:
    SPEC.loader.exec_module(prepare)


def test_draw_sample_uses_dcg_strata_not_jev_flags():
    assert prepare is not None, "prepare.py must expose the X7 frame functions"
    rows = [
        {
            "event_id": f"event-{index}",
            "dcg_decision": "deny" if index < 6 else "allow" if index < 12 else "warn",
            "jev_flag": bool(index % 2),
        }
        for index in range(15)
    ]
    first = prepare.draw_sample(rows, seed=20261005, per_stratum=3)
    flipped = [dict(row, jev_flag=not row["jev_flag"]) for row in rows]
    second = prepare.draw_sample(flipped, seed=20261005, per_stratum=3)

    assert [row["event_id"] for row in first] == [row["event_id"] for row in second]
    assert sum(row["dcg_decision"] == "deny" for row in first) == 3
    assert sum(row["dcg_decision"] == "allow" for row in first) == 3
    assert all(row["dcg_decision"] in {"allow", "deny"} for row in first)


def test_prior_sample_excludes_event_and_command_replays():
    assert prepare is not None, "prepare.py must expose the X7 frame functions"
    rows = [
        {"event_id": "same-event", "cmd_sha": "new-a"},
        {"event_id": "new-event", "cmd_sha": "old-command"},
        {"event_id": "fresh-event", "cmd_sha": "fresh-command"},
    ]
    prior = [
        {"event_id": "same-event", "cmd_sha": "old-a"},
        {"event_id": "old-event", "cmd_sha": "old-command"},
    ]

    remaining = prepare.exclude_prior_rows(rows, prior)

    assert [(row["event_id"], row["cmd_sha"]) for row in remaining] == [
        ("fresh-event", "fresh-command")
    ]


def test_dcg_failure_is_not_reclassified_as_a_decision():
    assert prepare is not None, "prepare.py must expose the X7 frame functions"
    assert prepare.parse_dcg_result('{"decision":"allow"}', 0) == "allow"
    assert prepare.parse_dcg_result('{"decision":"deny"}', 0) == "deny"
    assert prepare.parse_dcg_result('{"decision":"warn"}', 0) == "warn"
    assert prepare.parse_dcg_result('{"decision":"allow"}', 1) == "error"
    assert prepare.parse_dcg_result("not-json", 0) == "error"


def test_event_ids_are_repeatable_and_distinguish_duplicate_events():
    rows = [
        {"ts": "2026-10-06T00:00:00.000Z", "session": "session-a", "cmd_sha": "hash-a"},
        {"ts": "2026-10-06T00:00:00.000Z", "session": "session-a", "cmd_sha": "hash-a"},
    ]

    first = prepare.assign_event_ids(rows)
    second = prepare.assign_event_ids(rows)

    assert first[0]["event_id"] == second[0]["event_id"]
    assert first[1]["event_id"] == second[1]["event_id"]
    assert first[0]["event_id"] != first[1]["event_id"]


def test_transcript_join_requires_same_session_and_exact_command_hash():
    command = "echo x7-source-fixture"
    command_hash = prepare.sha256(command.encode("utf-8"))
    events = [
        {"event_id": "event-a", "session": "session-a", "cmd_sha": command_hash},
        {"event_id": "event-b", "session": "session-b", "cmd_sha": command_hash},
    ]
    calls = [{"session": "session-a", "command": command}]

    joined = prepare.match_command_occurrences(events, calls)

    assert joined[0]["source_match"] == "matched"
    assert joined[1]["source_match"] == "unreadable"


def test_committed_privacy_filters_match_and_reject_at_the_secret_boundary():
    filters = prepare.load_privacy_filters()

    assert prepare.privacy_exclusion("clutter", filters) == "private"
    assert prepare.privacy_exclusion("echo sk-" + "A" * 20, filters) == "secret"
    assert prepare.privacy_exclusion("echo sk-" + "A" * 19, filters) is None
    assert prepare.privacy_exclusion("printf ok", filters) is None
    assert prepare.privacy_exclusion("x" * (prepare.MAX_COMMAND_CHARS + 1), filters) == "too-large"


def test_privacy_filter_long_near_miss_is_bounded_and_timed():
    import time

    filters = prepare.load_privacy_filters()
    near_miss = "x" * 50_000 + "-----BEGIN " + "A" * 50_000 + "X"
    started = time.perf_counter()
    assert prepare.privacy_exclusion(near_miss, filters) is None
    assert time.perf_counter() - started < 1.0


def test_frame_manifest_reports_missing_transcript_sessions(monkeypatch, tmp_path):
    assert prepare is not None
    prereg = tmp_path / "prereg.md"
    filters = tmp_path / "filters.py"
    hook = tmp_path / "hook.ts"
    prior = tmp_path / "prior.jsonl"
    source_log = tmp_path / "gate-observe.jsonl"
    for path in (prereg, filters, hook, prior, source_log):
        path.write_text("", encoding="utf-8")
    monkeypatch.setattr(prepare, "PREREG", prereg)
    monkeypatch.setattr(prepare, "FILTER_SOURCE", filters)
    monkeypatch.setattr(prepare, "HOOK_SOURCE", hook)
    monkeypatch.setattr(prepare, "_prereg_commit", lambda: "committed-prereg")
    monkeypatch.setattr(
        prepare,
        "_read_observe_rows",
        lambda state_dir, cutoff: (
            [{"event_id": "event-a", "ts": "2026-10-06T00:00:00Z", "session": "session-a", "cmd_sha": "sha-a"}],
            [source_log],
            prepare.Counter(through_cutoff=1),
        ),
    )
    monkeypatch.setattr(
        prepare,
        "_joined_commands",
        lambda rows, cutoff: ({}, 2, "transcript-sha", set()),
    )
    monkeypatch.setattr(prepare, "load_privacy_filters", lambda: (None, None))

    frame, manifest = prepare._build_frame(
        "2026-10-06T01:00:00Z", tmp_path, prior, 1.0
    )

    assert manifest["missing_transcript_sessions"] == 2
    assert manifest["non_fleet_rows"] == 1
    assert manifest["dcg_decision_counts"] == {"unreadable": 1}
    assert frame == [{"event_id": "event-a", "cmd_sha": "sha-a", "dcg_decision": "unreadable"}]


def test_dcg_result_with_unhashable_decision_is_an_error():
    assert prepare is not None
    assert prepare.parse_dcg_result('{"decision":[]}', 0) == "error"


def test_frame_command_prints_missing_transcript_count(monkeypatch, tmp_path, capsys):
    assert prepare is not None
    frame_path = tmp_path / "frame.jsonl"
    manifest_path = tmp_path / "frame-manifest.json"
    metadata = {
        "frame_rows": 0,
        "frame_sha256": prepare.sha256(b""),
        "dcg_decision_counts": {},
        "prior_excluded": 0,
        "non_fleet_rows": 0,
        "missing_transcript_sessions": 2,
        "cutoff_utc": "2026-10-06T01:00:00Z",
    }
    monkeypatch.setattr(prepare, "FRAME_PATH", frame_path)
    monkeypatch.setattr(prepare, "FRAME_MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(prepare, "_require_committed_clean", lambda paths: "input-commit")
    monkeypatch.setattr(prepare, "_prereg_commit", lambda: "prereg-commit")
    monkeypatch.setattr(
        prepare,
        "_git",
        lambda *args: prepare.subprocess.CompletedProcess(
            args, 0, stdout="2026-10-05T00:00:00+00:00", stderr=""
        ),
    )
    monkeypatch.setattr(prepare, "_build_frame", lambda *args: ([], metadata))

    result = prepare._frame_command(
        prepare.argparse.Namespace(
            cutoff="2026-10-06T01:00:00Z",
            state_dir=str(tmp_path),
            prior_manifest=str(tmp_path / "prior.jsonl"),
            dcg_timeout=1.0,
        )
    )

    assert result == 0
    assert prepare.json.loads(capsys.readouterr().out)["missing_transcript_sessions"] == 2
    assert prepare.json.loads(manifest_path.read_text(encoding="utf-8")) == metadata


def test_pack_command_reconstructs_to_private_owned_scratch(monkeypatch, tmp_path, capsys):
    assert prepare is not None
    repo = tmp_path / "repo"
    scratch = repo / "var" / "agent-tmp" / "owned"
    scratch.mkdir(parents=True)
    scratch.chmod(0o700)
    (scratch / ".owner").write_text("pid=1 label=test\n", encoding="utf-8")
    monkeypatch.setattr(prepare, "ROOT", repo)
    monkeypatch.setattr(prepare, "_require_committed_clean", lambda paths: "input-commit")

    command = "echo private-pack-test"
    event_id = "event-a"
    command_hash = prepare.sha256(command.encode("utf-8"))
    frame_row = {"event_id": event_id, "cmd_sha": command_hash, "dcg_decision": "allow"}
    sample_row = {**frame_row, "stratum": "allow"}
    frame_text = prepare.canonical_jsonl([frame_row])
    sample_text = prepare.canonical_jsonl([sample_row])
    frame_path = repo / "work" / "x7-gate-rules" / "frame.jsonl"
    frame_manifest_path = repo / "work" / "x7-gate-rules" / "frame-manifest.json"
    sample_path = repo / "work" / "x7-gate-rules" / "sample.jsonl"
    sample_manifest_path = repo / "work" / "x7-gate-rules" / "sample-manifest.json"
    monkeypatch.setattr(prepare, "FRAME_PATH", frame_path)
    monkeypatch.setattr(prepare, "FRAME_MANIFEST_PATH", frame_manifest_path)
    monkeypatch.setattr(prepare, "SAMPLE_PATH", sample_path)
    monkeypatch.setattr(prepare, "SAMPLE_MANIFEST_PATH", sample_manifest_path)
    prior_path = tmp_path / "prior.jsonl"
    prior_path.write_text("", encoding="utf-8")
    for path, content in (
        (frame_path, frame_text),
        (
            frame_manifest_path,
            prepare.json.dumps({
                "frame_sha256": prepare.sha256(frame_text.encode()),
                "prior_manifest_sha256": prepare.sha256(prior_path.read_bytes()),
            }),
        ),
        (sample_path, sample_text),
        (
            sample_manifest_path,
            prepare.json.dumps({
                "frame_sha256": prepare.sha256(frame_text.encode()),
                "sample_sha256": prepare.sha256(sample_text.encode()),
                "cutoff_utc": "2026-10-06T01:00:00Z",
            }),
        ),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    event = {"event_id": event_id, "session": "session-a", "cmd_sha": command_hash}
    monkeypatch.setattr(
        prepare,
        "_read_observe_rows",
        lambda state_dir, cutoff: ([event], [], prepare.Counter()),
    )
    monkeypatch.setattr(
        prepare,
        "_joined_commands",
        lambda rows, cutoff: (
            {event_id: {"event_id": event_id, "_command": command}},
            0,
            "transcript-sha",
            {event_id},
        ),
    )
    monkeypatch.setattr(prepare, "privacy_exclusion", lambda command, filters: None)
    output = scratch / "commands.jsonl"
    tampered_frame_text = frame_text.replace('","', '", "')
    assert tampered_frame_text != frame_text
    frame_path.write_text(tampered_frame_text, encoding="utf-8")
    rejected_output = scratch / "rejected-commands.jsonl"
    try:
        prepare._pack_command(
            prepare.argparse.Namespace(
                output=str(rejected_output),
                state_dir=str(tmp_path),
                prior_manifest=str(prior_path),
            )
        )
    except ValueError as error:
        assert "frame SHA-256" in str(error)
    else:
        assert False, "pack accepted a frame that disagrees with its manifest"
    assert not rejected_output.exists()
    frame_path.write_text(frame_text, encoding="utf-8")
    result = prepare._pack_command(
        prepare.argparse.Namespace(
            output=str(output),
            state_dir=str(tmp_path),
            prior_manifest=str(prior_path),
        )
    )

    assert result == 0
    assert output.read_text(encoding="utf-8") == prepare.canonical_jsonl(
        [{"event_id": event_id, "cmd_sha": command_hash, "command": command}]
    )
    assert prepare.stat.S_IMODE(output.stat().st_mode) == 0o600
    assert command not in capsys.readouterr().out
    prior_path.write_text('{"event_id":"different-prior","cmd_sha":"different-hash"}\n', encoding="utf-8")
    stale_output = scratch / "stale-prior-commands.jsonl"
    try:
        prepare._pack_command(
            prepare.argparse.Namespace(
                output=str(stale_output),
                state_dir=str(tmp_path),
                prior_manifest=str(prior_path),
            )
        )
    except ValueError as error:
        assert "prior manifest changed" in str(error)
    else:
        assert False, "pack accepted a prior manifest changed after frame freeze"
    assert not stale_output.exists()
