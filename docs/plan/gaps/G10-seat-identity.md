# G10 / ID1 — Caller-bound seat identity

- **seat:** `jev:0.2`
- **worker:** AmberWillow (legacy `resolve-pane` result for `$TMUX_PANE=%18`; not accepted as G10 ownership proof)
- **prompt:** `ASSIGN-GAPSECTIONS.md@de15f39f6fb1df7d7857b858bf93854ccc2014c9ccc6736d7b7166ff1bc193d9`
- **plan:** CORE8-R2, `c0455745`
- **status:** Planning only. No `omp-kit` implementation or bead mutation in this section.

## 1. Problem

Identity currently comes from a caller-supplied pane id or name, not an authenticated binding to the process making the call. In the recorded incident, AmberWillow (`%18`) passed the director's `%56` to `resolve_pane_identity`, received `BrownGoose`, then reserved and filed a deliverable as the director; another worker supplied `BrownGoose` from a filename. The resulting reservation blocked the worker's own grade file, and the director had to release holds it had not taken. The same evidence records incorrect self-reported `session_uuid` values for two of four workers. [BrownGoose-pane-identity.md:6-10; AM 48388]

The recorded identity doctor saw 45 panes, 32 without an identity file, a shared name, and stale names, but returned `rc=0`. [BrownGoose-pane-identity.md:15; AM 48412] The later process census distinguishes ordinary panes from OMP agents: 45 tmux panes, 43 identity-bearing pane IDs, 139 identity files; nine names span multiple seats, 35 pane IDs have multiple recorded names, and two identified OMP panes lack an identity-file name (`%37`, `%114`). `%114` is an OMP process with no `TMUX_PANE`; the 27 session-bearing OMP agent processes did report matching `TMUX_PANE` values. These counts are from different views: do not treat every shell pane without an identity file as an unbound agent. [AmberWillow-G24b-identity.md:7-9, 61-66]

Item 15 also requires seat-addressed sends. Icy reported `omp-kit send <session> <seat>` returning `NOT_DELIVERED`. That report establishes the failure, not whether the cause is target resolution or delivery proof. [ASSIGN-GAPSECTIONS.md:7, 28-29; AM 48412, 48444]

## 2. Why it matters

A wrong identity turns reservations, messages, bead actor attribution, and deliverable authorship into actions by the wrong worker. It can block unrelated work and make self-review or self-close invisible. The observed incident demonstrates both impersonation and operational impact; a filename, packet callback target, pane number, or caller-provided name is not identity evidence. [BrownGoose-pane-identity.md:7-14; AM 48388]

## 3. Requirement (observable)

1. `omp-kit whoami` MUST derive the caller's seat from its own process context, never from a requested pane/name. Return one record containing `name`, `seat`, `pane_id`, tmux socket/server identity, OMP `agent_pid`, process start time, and registration generation. `TMUX_PANE` is an input to verify against the pane/process graph, not sufficient proof by itself. [BrownGoose-pane-identity.md:17-25]
2. One authoritative Agent Mail binding MUST bind `(tmux socket, server pid, pane id, agent pid, agent start time)` to the registered name and generation. Pane-number reuse or agent restart MUST make the old binding stale; a write with a stale/mismatched registration token MUST be refused. Do not add a second local identity registry. [BrownGoose-pane-identity.md:12-25]
3. Every identity-dependent write MUST obtain the caller binding internally. Agent Mail mutations MUST present the matching registration proof; `br` actor and tool-authored `worker`/`session_uuid`/commit-trailer metadata MUST be derived from the same binding. Callers MUST NOT choose `agent_name` or `--actor` to assert who they are. [BrownGoose-pane-identity.md:12-25; ID1 bead `ompkit-rc-epic-land-fix-release-dogfood-rz5.108`]
4. `doctor --scope identity` MUST inspect actual OMP agent processes, not classify every non-agent tmux pane as an unbound worker. It MUST report a non-zero exit for unbound, duplicate, stale, or process-mismatched bindings. A caller-bound `whoami` or identity-resolution API MUST refuse a request to assert another pane as the caller. Inspection failure MUST be `UNVERIFIED`/non-zero, never a healthy result. An identity-scope change MUST NOT silently change other doctor scopes. [BrownGoose-pane-identity.md:25-32; origin `src/cli.ts`:539-563]
5. A send target is distinct from sender identity. `omp-kit send <session> <seat> <message>` MUST resolve the requested seat to one current pane/process binding before sending; ambiguous, absent, stale, or mismatched targets MUST be refused without sending. Preserve a distinct `PENDING_SUBMIT` result; do not call it `OK` or `CONSUMED`. Only the target agent's own session JSONL is the independent consumption oracle. [AM 48444; origin `src/send.ts`:77-105; G25 matrix:13-18]

## 4. Existing seam

The clean `omp-kit-companion` `origin/main` snapshot at `b3cda9a4ac5149907c7e9f922e1a3bbdc51a4531` already has a read-only identity inspector. `defaultPaneIdentity` lists tmux panes and calls `am agents resolve-pane --pane <id>`; `inspectPaneIdentity` groups returned names, finds missing names/shared names/stale registrations, and emits status. It does not bind the caller to an OMP process PID/start time or registration generation. [origin `src/diagnostics.ts`:573-660]

The CLI routes `doctor --scope identity` through the findings, but only `health` uses strict overall status for its exit code; `doctor` otherwise returns code 0 unless the `kit` or `manifest` finding fails. This matches the red test below. [origin `src/cli.ts`:493, 516-524, 539-563]

The existing send command parses `SESSION PANE MESSAGE`, passes the raw pane operand to `proveSend`, and maps every non-`OK` result to `NOT_DELIVERED`. `proveSend` sends to the raw pane and looks for its marker in tmux capture; it can distinguish `PENDING_SUBMIT`, but the command collapses that status. Screen presence is not proof of receiver consumption. Reuse the send path after target resolution; use G24a's target-session-JSONL oracle for the consumed verdict rather than inventing a second delivery mechanism. [origin `src/cli.ts`:2542-2571; origin `src/send.ts`:60-105; G25 matrix:13-18]

The tracker record for ID1 is `ompkit-rc-epic-land-fix-release-dogfood-rz5.108` (“agent identity primitive for every repo: pane identity at spawn, br actor injected and enforced, Agent trailer on commits, grader != implementer guard”). The bead is the implementation owner; this section defines the G10 seat-identity contract, not a second identity workstream. [read-only `br show --no-auto-import --no-auto-flush`]

## 5. Design and rejected alternatives

**Design:** Keep Agent Mail as the sole identity authority. Add one shared caller-bound resolver used by `whoami`, identity doctor, and identity-dependent writes. It reads the current caller's `TMUX_PANE`, verifies the tmux socket/server and pane, locates the OMP process by process ancestry/command, and captures PID plus start time. It resolves only that tuple against the current Agent Mail registration generation. Keep the registration token out of `whoami` output; use it internally on writes. Missing process, ambiguous ancestry, stale generation, or Agent Mail failure is a refusal/unknown result, never a fallback to a filename or pane number. [BrownGoose-pane-identity.md:17-25]

For `doctor --scope identity`, enumerate actual OMP agent processes and compare each with exactly one current binding. Distinguish non-agent panes from agent panes; report unbound, duplicate, stale, mismatched, and unavailable evidence explicitly. Set the exit code from this scope's status only. For sends, treat caller identity and destination seat as separate values: resolve the destination seat to a current pane/process binding, then pass only its canonical pane target to the existing send mechanism. Preserve `PENDING_SUBMIT`; G24a owns the submitted/consumed classification and its target-session-JSONL oracle. [origin `src/diagnostics.ts`:573-660; origin `src/cli.ts`:539-563, 2542-2571; G25 matrix:13-18]

**Rejected:**

- Accepting a caller-provided pane id/name as the sender: directly enabled the `%18` → `%56` impersonation. [BrownGoose-pane-identity.md:7, 13]
- Treating pane number or identity filename as a stable key: pane numbers are reused and the observed files contain multiple names per pane. [BrownGoose-pane-identity.md:14; AmberWillow-G24b-identity.md:63]
- Treating `TMUX_PANE` alone as proof: it identifies a pane but not which OMP process generation is authorized to act there; `%114` also had no `TMUX_PANE`. Use it as an independent consistency check with process ancestry and start time. [BrownGoose-pane-identity.md:17-18; AmberWillow-G24b-identity.md:64-66]
- Creating a new local registry or watcher: Agent Mail is already the identity authority; a second store creates another source of truth. [BrownGoose-pane-identity.md:12-25]
- Treating a visible tmux marker as consumed: G25 names the receiver's own session JSONL as the independent oracle and a composer-only marker as `PENDING_SUBMIT`. [G25 matrix:13-18]
- Fixing only the doctor exit code: it would leave the observed forged reservations, sends, actors, and metadata unchanged. [BrownGoose-pane-identity.md:7-15; ID1 bead `.108`]

## 6. Dependencies

- **ID1:** `ompkit-rc-epic-land-fix-release-dogfood-rz5.108` — implementation owner for the identity primitive, actor injection, commit attribution, and reviewer separation. Read through the `omp-kit` tracker; do not push the test-only commit `19bf7353`. The identity tests and implementation must land together in a bead-bearing commit. [read-only `br show`; current task instruction]
- **G24b:** caller-process identity row; supplies the live process-bound acceptance cases and test ownership. [G25 matrix:16]
- **G24a:** send consumption state and target-session-JSONL oracle; G10 resolves the seat, G24a proves consumption. [G25 matrix:13-15]
- **G25:** reuse its identity and send rows; do not duplicate its delivery-proof suite. [BrownGoose-G25-test-matrix-jev.md:11-18]
- **Chief integration:** item 15 and adoption of this section. [AM 48412, 48445; ASSIGN-GAPSECTIONS.md:1-7]

## 7. Test matrix rows

| requirement | test classes | positive case | planted-red / negative | independent oracle | owner | pass bar | run surface | when |
|---|---|---|---|---|---|---|---|---|
| Caller-bound `whoami` and generation | unit over observed process rows; live CLI; restart test | Each of five workers returns its own seat/name and process tuple, matching `ps eww` `TMUX_PANE` and the registered generation. | (1) request director `%56` as self; (2) wrong/missing `TMUX_PANE`; (3) same-pane agent restart with old token; (4) duplicate name on two live processes; (5) unbound OMP process. | `ps` environment/process ancestry + tmux socket/server/pane data; Agent Mail registration response/token validation. Never use the caller's requested name as oracle. | Test: CyanPeak; impl: ID1 owner. | All five negatives refuse; all five positive panes resolve uniquely; no stale generation accepted. | `bun test tests/cli/identity-seat.test.ts` + fresh OMP panes; no paid calls. | Before ID1 land. |
| Identity doctor status | targeted CLI tests; live scoped doctor | Clean current worker/process bindings return identity `OK`, exit 0. | Unbound OMP process, duplicate current name, stale PID/start, and unavailable process/Agent Mail probe each return non-zero and explicit evidence; ordinary non-agent shell panes do not count as unbound workers. | Independent tmux/process inventory plus Agent Mail current registrations; CLI JSON/status and exit code. | Test: CyanPeak; impl: ID1 owner. | 0 false-OK cases; non-identity doctor scopes unchanged. | `omp-kit doctor --scope identity --project <fixture> --json`; fresh-pane smoke. | Before ID1 land. |
| Seat-addressed send | unit over target resolution; G24a no-mock/e2e consumption row | A valid `SESSION SEAT` resolves to the intended process-bound pane; accepted message appears in that recipient's session JSONL. | Unknown, ambiguous, stale, or reused seat refuses before send; a composer-only marker is `PENDING_SUBMIT`, not `OK`/`CONSUMED`; a missing marker remains `NOT_DELIVERED`. | Tmux/process topology for target selection; target agent's own session JSONL for consumption. | Test: GoldRiver (G24a); impl: ID1 owner. | No wrong-seat sends; 0 false-OKs on G24a's three negative goldens; status matches the receiver log. | `omp-kit test` / CI for G24a; targeted seat-resolution test for G10. | Before ID1 land. |
| Identity-dependent write authorization | unit over caller-bound client; isolated Agent Mail/`br`/git fixtures | A valid current binding authorizes a reservation and stamps the same `name`/generation into the tool-produced actor and commit metadata. | Caller-supplied `agent_name`/`--actor`, stale token, or another pane's tuple is refused before mutation; no reservation or commit is created. | Agent Mail server response; resulting actor and commit object/trailer in an isolated repo, compared with OS/tmux identity—not caller-provided output. | Test: CyanPeak; impl: ID1 owner. | 0 accepted mismatched writes; every positive write maps to the same binding; no live shared tracker or repo writes. | Targeted `omp-kit` tests in isolated fixtures. | Before ID1 land. |

### Current red evidence (not a pass)

Run from `/Users/josh/Developer/omp-kit-companion` with `TMPDIR` set to the owned `var/agent-tmp/g24b-red.47555` directory:

```sh
OMP_KIT_BIN=/Users/josh/.local/bin/omp-kit nice -n 10 bun test tests/cli/identity-seat.test.ts
```

The test helper invokes the installed CLI with fixture `tmux`/`am` executables (`tests/cli/identity-seat.test.ts:27-59`); the cases use census-derived pane rows `%37`, `%0`, and `%20` (`:12-17`). This is a real targeted CLI regression run against the installed binary, but not a live-fleet test. Both finding assertions pass; both exit-code assertions fail because identity-scope doctor returns 0. Exact output:

```text
bun test v1.4.0 (34cbb9a40)

tests/cli/identity-seat.test.ts:
72 | 	expect(pure.status).not.toBe("OK");
73 | 	expect(pure.evidence?.no_file_panes).toEqual([UNBOUND_AGENT.id]);
74 | 
75 | 	const result = doctor([UNBOUND_AGENT], null);
76 | 	expect(identityFinding(result.envelope).status).not.toBe("OK");
77 | 	expect(result.exitCode).not.toBe(0);
                                  ^
error: expect(received).not.toBe(expected)

Expected: not 0

      at <anonymous> (/Users/josh/Developer/omp-kit-companion/tests/cli/identity-seat.test.ts:77:30)
(fail) RED-1: an unbound agent pane is non-OK and the doctor exits non-zero [756.22ms]
84 | 	expect(pure.status).toBe("FAIL");
85 | 	expect(pure.evidence?.shared).toEqual([{ name: "CloudyPuma", panes: ["%0", "%20"] }]);
86 | 
87 | 	const result = doctor(SHARED_AGENTS, "CloudyPuma");
88 | 	expect(identityFinding(result.envelope).status).toBe("FAIL");
89 | 	expect(result.exitCode).not.toBe(0);
                                  ^
error: expect(received).not.toBe(expected)

Expected: not 0

      at <anonymous> (/Users/josh/Developer/omp-kit-companion/tests/cli/identity-seat.test.ts:89:30)
(fail) RED-2: one census identity on multiple seats fails and the doctor exits non-zero [616.22ms]

 0 pass
 1 todo
 2 fail
 8 expect() calls
Ran 3 tests across 1 file. [1409.00ms]

test_exit_code=1
```

The third row is `test.todo` because the caller-bound `whoami` API does not exist in the inspected source; it is not claimed as exercised. [tests/cli/identity-seat.test.ts:92; AmberWillow-G24b-identity.md:68-80]

The test-only commit `19bf7353` is local and unpushed. The runner override used for this run selects the installed CLI; the pending test changes must co-land with ID1. An earlier push attempt was refused because the process identity was `worker-1`/`AGENT_NAME` unset while this pane's reservation was held as AmberWillow, creating a self-collision; the task instruction also prohibits pushing the test-only commit. Do not bypass or release another worker's reservation to land it. [current session tool output; user instruction]

Socraticode MCP was unavailable (`No such tool`); its health probe was healthy but no semantic queries ran (`socraticode_queries=0`). Source claims above come from the pinned `origin/main` snapshot and captured local evidence, not semantic-index results. [current session probe; `AmberWillow-G24b-identity.md:84`]

## 8. Close condition

A non-author verifier runs the targeted identity-seat tests against the resulting installed CLI and observes all required cases GREEN, including the two current REDs and caller-bound `whoami`; then runs `doctor --scope identity` in a fresh session with one healthy positive and planted borrowed-seat, restarted-generation, duplicate-name, and unbound-agent negatives. Verify each refusal against tmux/process facts and Agent Mail results. For send, verify the intended seat from topology and consumption from the recipient's session JSONL; screen capture alone is insufficient. The verifier confirms non-identity doctor behavior is unchanged, checks the bead-bearing combined commit SHA, and records the result. No live Jev calls or model-cost claim are required. [G25 matrix:13-18; G10 acceptance: BrownGoose-pane-identity.md:27-32]

## 9. Bead card

**Existing implementation bead:** `ompkit-rc-epic-land-fix-release-dogfood-rz5.108` — ID1 agent identity primitive.

- **Why:** observed caller-selected `%56` identity caused false director authorship and reservations; the identity doctor returned success on findings; seat-addressed send reported `NOT_DELIVERED`. [BrownGoose-pane-identity.md:7-15; AM 48388, 48444]
- **Acceptance:** implement the caller-bound process tuple and single Agent Mail generation; reject borrowed/stale/missing identities on all identity-dependent writes; make identity doctor non-zero on non-OK identity status while excluding non-agent panes; resolve send destinations by current seat and preserve delivery states; satisfy all rows in §7 using independent OS/tmux/Agent Mail/receiver-session oracles.
- **Dependencies:** G24b identity; G24a send consumption; G25 test matrix.
- **Test rows:** §7, rows 1–3. Keep test `19bf7353` unpushed and co-land its test changes with the ID1 implementation under a subject containing this bead ID. [read-only `br show`; current task instruction]

## 10. Open questions

1. **Should `SESSION SEAT` accept a canonical tmux seat (`session:window.pane`), a registered worker name, or both?** Choose one unambiguous selector; never use the selector as sender identity. **Owner:** BrownGoose, `jev:0.1` (chief/integration). [AM 48412, 48445]
2. **Does Agent Mail validate its existing registration token against the process tuple on reservation, send, and release, or is an API change required?** Do not ship a client-only token check as proof. **Owner:** BrownGoose, `jev:0.1` (chief; assign the ID1 implementation owner to verify the server contract). [BrownGoose-pane-identity.md:23]
3. **What process-ancestry rule identifies the OMP child when the current command is a shell/tool subprocess, and how is an ambiguous tree represented?** Require `UNVERIFIED`/refusal on ambiguity; do not guess. **Owner:** BrownGoose, `jev:0.1` (chief; assign the ID1 implementation owner to verify the process contract). [BrownGoose-pane-identity.md:18]
