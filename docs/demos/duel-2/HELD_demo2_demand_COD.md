# Demo-2 demand resolution — named practitioner complaint

Status: **RECOVERED from the demand-evidence hold; score unchanged.**
Candidate: Demo-2 admission screen, reconciled demand score 700.
Named practitioner: **Jörg Michno (`joergmichno`)**, Software Developer | GenAI & AI Security | Building tools to keep AI agents safe.
Primary source: [GenAI Toolbox issue #2844](https://github.com/googleapis/mcp-toolbox/issues/2844),
opened 2026-03-25.

## Verbatim complaint

The issue title is:

> Security Advisory: Prompt Injection Risk via Database Content in LLM Context

Jörg Michno's summary says:

> GenAI Toolbox connects AI agents directly to databases (PostgreSQL, MySQL, BigQuery, Spanner,
> MSSQL) and loads query results into the LLM context. Since database content can contain
> **attacker-controlled data**, any database row or field value can serve as a prompt injection
> vector that hijacks the AI agent's behavior.

The attack path is explicit:

> 1. Attacker inserts malicious content into a database field (e.g., a user comment, product
> description, or support ticket)
> 2. AI agent queries the database via GenAI Toolbox → attacker-controlled content enters the LLM
> context
> 3. Injection instructs the AI to execute write operations, exfiltrate data from other tables, or
> modify records

The impact list names:

> **Data Exfiltration**: AI could be instructed to query sensitive tables and return results to the
> attacker via write operations

> **Data Manipulation**: Injected instructions could cause the AI to UPDATE or DELETE records

> **Privilege Escalation**: Database queries run with the configured service account permissions,
> which may exceed what the end user should access

The recommended remediation includes:

> Implement output sanitization on query results before passing to LLM context

This is a named practitioner, a filed security issue, a concrete tool-result admission path, and a
specific proposed defense. It is not a generic vendor page or a benchmark assertion.

## Fit to Demo-2

The complaint matches Demo-2's whole-AI demand question:

- **Input boundary:** database query results are untrusted bytes;
- **Admission boundary:** those bytes enter LLM context;
- **Action risk:** injected text can induce writes, exfiltration, or record modification;
- **Desired control:** sanitize or screen output before it enters context;
- **Named buyer:** an engineer building or securing an agent/database integration.

It is broader than a file-read prompt injection. The same failure class applies to database rows,
comments, product descriptions, support tickets, browser results, MCP output, and retrieval content.
The source therefore recovers the “who downloads it and why” hold without requiring a calibration
claim. It does not prove Demo-2's detection rate, false-positive rate, or product adoption.

## What the source does not establish

This complaint does not establish:

1. that a Jev Noul beats a deterministic sanitizer or vendor guard;
2. that the proposed 0.80 policy threshold is calibrated;
3. that the source's recommended sanitization should block, withhold, or pass any particular row;
4. that the issue's threat model has a measured prevalence across deployments;
5. that the author adopted or would download this specific Demo-2 hook;
6. that a hosted guard such as Lakera or Prompt Shields is insufficient.

It is demand evidence, not a runtime proof. The source also does not mention calibration, confidence,
probability, or abstention. Any document turning this issue into evidence for the lane's calibration
thesis would be overstating it.

## Relationship to the current contract

Demo-2's contract is injection-only and shadow-first. The issue's recommended output sanitization is
compatible with the local prefilter boundary but is not identical to semantic injection judgment:

- deterministic local secret redaction protects credential bytes before any model call;
- Noul judges whether cleared tool-result content contains an instruction directed at the reading
  agent;
- shadow mode measures false positives before enforcement;
- the receipt must distinguish screened, would-block, admitted-silent, credential-redacted, malformed,
  and Jev-request counts.

The issue supports the admission-screen problem, especially the need to distinguish trusted schema
from untrusted content. It does not authorize sending raw secrets to Jev and does not excuse a
credential classifier. Demo-8 remains killed.

## Adjudication

**Verdict: demand hold recovered; Demo-2 score remains 700.**

The Q20 condition asked for one named practitioner, filed issue, or measured incident. Jörg Michno's
issue satisfies it with verbatim text and a direct runtime scenario. Per lane doctrine, resolving a
hold makes the candidate judgeable; it does not raise the demand score. The prior 700 remains the
recorded score, and later non-author proof must still establish a differentiated replay/action-scope
wedge against existing guards.

## Retry / next measurement

The next measurement is a synthetic database/tool-result corpus with:

- benign rows containing imperative language;
- attacker-controlled instructions in comments/product/support fields;
- forged policy/system text;
- cross-agent propagation;
- credential-shaped values that must be redacted before Jev;
- a synthetic side-effect sink proving block/hold happens before action;
- held-out labels and false-positive accounting.

The command must report detection recall, benign admission, false-positive rate, cost/latency,
block-before-side-effect rate, provenance coverage, and the credential-redaction skip count. If the
corpus cannot be assembled without sending real sensitive data, the candidate is HELD/UNASKABLE, not
killed. If a maintained vendor control already supplies the same replayable action-scope receipt,
that becomes the baseline rather than an automatic kill.

## Source record

| Field | Value |
|---|---|
| Author | Jörg Michno (`joergmichno`) |
| Profile | [github.com/joergmichno](https://github.com/joergmichno) |
| Bio | Software Developer \| GenAI & AI Security \| Building tools to keep AI agents safe |
| Issue | [googleapis/mcp-toolbox#2844](https://github.com/googleapis/mcp-toolbox/issues/2844) |
| Opened | 2026-03-25T08:25:50Z |
| State observed | Closed |
| Evidence type | Named filed security issue with attack path and remediation request |

## NO-CLAIM

No tool was installed, no database was queried, no model call was made, and no real secret or
attacker-controlled payload was sent. This resolves only Demo-2's named-user demand hold and leaves
its score, calibration, runtime safety, and measured lift unchanged.
