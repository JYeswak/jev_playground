# Held resolution — MU-H3 runtime-redaction voiced pain

Status: **RECOVERED from the voiced-pain hold; score remains 650.**
Candidate: MU-H3 sanitize-before-send, pane-3 authored.
Named practitioner: **Pablo Rodriguez (`paroque28`), Embedded Systems Engineer**.
Primary source: [Claude Code issue #39882](https://github.com/anthropics/claude-code/issues/39882), opened
2026-03-27, currently closed as not planned.
Search rule: this search was deliberately not framed around calibration, confidence, probabilities,
or withhold. It searched for practitioners describing runtime secret/redaction pain in their own
words.

## The complaint, verbatim

Pablo Rodriguez's issue is titled:

> `[FEATURE] PreApiCall / PostApiCall hooks to prevent secret exfiltration to API providers and attackers`

The issue begins with this direct statement:

> When using Claude Code, sensitive data can leave the user's machine through **two channels**:

It then names the first channel and the data involved:

> All code, file contents, command outputs, and user prompts are sent to the API. This includes:
> API keys and credentials embedded in configuration files; internal project and company names under
> NDA; employee names and email addresses (PII/GDPR); internal hostnames, IPs, and infrastructure
> details; proprietary business logic and trade secrets.

The issue states the operator need plainly:

> **The core need**: Organizations need the ability to **prevent sensitive data from leaving the
> machine through any channel** — whether to the API provider or to an attacker.

The complaint identifies a concrete runtime boundary failure, not a general security slogan. Under
“Why existing hooks are insufficient,” Rodriguez writes:

> The current hook system operates at the **tool level**, which creates fundamental gaps.

The issue's table says `PostToolUse` cannot modify output, and the author spells out the consequence:

> Because **PostToolUse cannot modify tool output**, there is no way to redact secrets from:
> `Read` tool results (file contents sent to the LLM), `Grep` search results, `Bash` command output,
> `Glob` file listings, `WebFetch` responses, or any future tool or MCP tool output.

The requested remedy is also specific:

> Add two new hook events that fire at the **API request/response level**.

For the pre-send boundary, the issue says:

> Fires **before** the Messages API request is sent to the upstream provider. The hook receives the
> full request body (all messages, tool results, system prompt) and can return a modified version.

And it gives the redaction use case:

> A redaction tool scans all content blocks and replaces sensitive values with tokens before
> anything leaves the machine.

This is a named practitioner's own complaint, an exact boundary, a list of affected paths, and a
proposed remedy. It directly satisfies the Q6 retry condition. The public profile identifies
`paroque28` as Pablo Rodriguez, an Embedded Systems Engineer:
[github.com/paroque28](https://github.com/paroque28).

## What this evidence actually proves

It proves external voiced pain for the runtime outbound-redaction boundary. It does **not** prove:

- that MU-H3's proposed Jev transport is the right implementation;
- that the problem occurs at a measured rate across agent platforms;
- that a deterministic scanner's recall is sufficient;
- that the issue's requested hooks will be implemented (the issue is closed as not planned);
- that a local proxy or Docker Agent redaction feature is inferior;
- that any calibration or probability claim matters to this practitioner.

The last boundary is deliberate. The complaint does not mention calibration, confidence, probability,
uncertainty, or a desire for a judgment model. It complains about **coverage and timing**: tool-level
hooks cannot modify the complete outbound request before provider transmission. I do not translate
that complaint into the lane's calibration vocabulary. The external evidence is valuable precisely
because it is not an echo of the conductor's thesis.

## Search record

The problem-first search used these unframed queries and followed the most concrete results:

- `agent tool output secret sent to LLM provider redaction GitHub issue`;
- `runtime tool result secret exfiltration API provider issue`;
- `Claude Code hook cannot modify tool output redact secrets`;
- `agent framework outbound request secret redaction practitioner complaint`.

The search surfaced several adjacent implementations and discussions, but the Claude Code issue was
the strongest named complaint because it contains a first-person product request, a concrete affected
surface, exact hook limitations, and a proposed end-to-end flow. The relevant source is not a vendor
claim about a feature; it is an issue opened by a named engineer asking for a missing safety boundary.

## Scope comparison with MU-H3

MU-H3 proposes a deterministic outbound sanitizer with:

- exact runtime-value and pattern/entropy detection;
- fixed-token redaction before provider serialization;
- fail-closed detector errors;
- per-call redaction counts and a receipt;
- coverage of tool results and provider-bound messages.

Rodriguez's complaint supports the **need for the boundary** and specifically names the failure of
post-tool hooks to modify outputs. It does not establish every MU-H3 design choice. In particular,
MU-H3 must still distinguish:

1. raw tool result versus persisted session history;
2. provider-bound model request versus direct tool/network egress;
3. registered exact secrets versus unknown credentials;
4. redaction before logs/traces versus only before the final API call;
5. safe placeholder restoration in local tool execution versus accidental provider exposure.

The issue itself mentions a local proxy via `ANTHROPIC_BASE_URL` as an existing workaround and lists
streaming, TLS, process lifetime, discoverability, and failure handling drawbacks. That is a real
baseline, not proof that a new transport wins. MU-H3's next demand/proof work must compare the
transport to that workaround and to maintained SDK filters without sending any real secret.

## Adjudication

**Verdict: the voiced-pain hold is resolved; MU-H3 remains HELD at score 650.**

The named practitioner and verbatim complaint satisfy the queue's one-citation condition. The score
does not move: resolving “does anyone publicly voice this pain?” answers judgeability, not product
value. The external source describes runtime redaction coverage and timing, not a Jev-specific
calibration advantage. A future non-author demand/rung assessment must use the complaint as evidence
of pain while keeping implementation and measured-lift questions open.

This result also corrects the lane's prior framing risk. The evidence is **positive for runtime
redaction pain**, but **silent on calibration**. Any document that cites this issue as proof of a
calibrated-probability market need would be overstating it.

## Retry and next evidence condition

The next condition is a shared, redaction-safe corpus of synthetic tool results and provider-bound
request fixtures. It must measure raw-secret bytes crossing each boundary, detector misses, false
redactions, persistence/log exposure, and request latency. A real provider key is not needed; the
fixture can use deterministic sentinels and an asserting sink.

If a future search finds a maintained platform hook that already provides the same complete
pre-API-call transformation and receipt, it becomes the baseline. It does not erase Rodriguez's
complaint; it changes the head-to-head. If no reproducible synthetic corpus can exercise the complete
request boundary, the candidate becomes HELD/UNASKABLE on measurement, never killed because the one
issue was insufficiently broad.

## Sources

- [Claude Code issue #39882](https://github.com/anthropics/claude-code/issues/39882), author `paroque28`,
  Pablo Rodriguez, opened 2026-03-27, closed as not planned.
- [Pablo Rodriguez GitHub profile](https://github.com/paroque28), bio: Embedded Systems Engineer.
- [OpenAI Agents JS running agents](https://openai.github.io/openai-agents-js/guides/running-agents/),
  adjacent final model-input filter baseline, not the source of the complaint.
- [Docker Agent schema](https://github.com/docker/docker-agent/blob/main/agent-schema.json), adjacent
  redaction implementation surfaced during search, not used as evidence of practitioner pain.

## NO-CLAIM

No package was installed, no hook was enabled, no secret was sent, and no runtime rate was measured.
The result is one externally voiced, named complaint with verbatim evidence. It recovers the Q6 hold
condition only; it does not raise MU-H3's score, establish calibration demand, or prove MU-H3's
implementation.
