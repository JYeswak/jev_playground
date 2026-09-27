# Draft metadata — do not paste this header

Target: upstream issue #25
Title: webscreen catch rate does not transfer across public prompt-injection sets

---

## What happened, and what you expected instead

On the current Hermes Jev Skills repository, `jevkit.webscreen.screen()` caught 15/40 label=1 rows from the public S-Labs prompt-injection test split and 16/40 label=1 rows from the public deepset/prompt-injections test split in one run. The same screening function reports a high catch rate on the project's own planted attack family in the web-screen scorecard. I expected the scorecard to distinguish in-distribution planted recall from held-out public-set recall, rather than implying that the planted score transfers to public attacks.

This report is about measurement/generalization reporting, not a request to raise the threshold or to claim that either public set represents all web attacks.
### Expected

The own-attack scorecard should be described as in-distribution planted recall. A deployment-facing report should separately measure and label recall on public held-out attack sets.

### Observed

The clean-clone repro returned 15/40 flagged on S-Labs and 16/40 on deepset label=1 rows, while using the same jevkit.webscreen.screen() path and pinned threshold. The public-set observations are lower than the own-family scorecard and have their own sampling uncertainty.

## Josh's own-words sentence (owner fills before filing)

>

## The smallest way to see it again

This uses Python 3.9+, the repository's standard-library-only `jevkit`, and public Hugging Face dataset rows. It does not install Hermes or paste an API key. Set `TYPESAFE_API_KEY` in the environment using your normal secret manager before running it.

```bash
git clone https://github.com/kerpopule/hermes-jev-skills
cd hermes-jev-skills
cat > repro_issue25.py <<'PY'
import json
import urllib.parse
import urllib.request
from collections import Counter
from jevkit import webscreen

UA = "hermes-issue-25-repro/1.0"

def rows(dataset, split="test", label=1, count=40):
    selected = []
    for offset in range(0, 1000, 100):
        query = urllib.parse.urlencode({
            "dataset": dataset, "config": "default", "split": split,
            "offset": offset, "length": 100,
        })
        request = urllib.request.Request(
            "https://datasets-server.huggingface.co/rows?" + query,
            headers={"User-Agent": UA},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        selected.extend(
            item["row"]["text"]
            for item in payload["rows"]
            if item["row"].get("label") == label
        )
        if len(selected) >= count:
            return selected[:count]
    raise RuntimeError(f"only {len(selected)} label={label} rows for {dataset}")

def one(text):
    result = json.dumps({"results": [{"content": text}]})
    return webscreen.screen("web_extract", result)

def run(dataset):
    verdicts = [one(text) for text in rows(dataset)]
    return {
        "dataset": dataset,
        "rows": len(verdicts),
        "flagged": sum(bool(item.get("flagged")) for item in verdicts),
        "status": dict(Counter(item.get("status") for item in verdicts)),
        "judged": sum(item.get("judged", 0) for item in verdicts),
    }

print(json.dumps([
    run("S-Labs/prompt-injection-dataset"),
    run("deepset/prompt-injections"),
], indent=2, sort_keys=True))
PY
python3 repro_issue25.py
```

One observed run on the current repository HEAD returned:

```json
[
  {"dataset": "S-Labs/prompt-injection-dataset", "flagged": 15, "judged": 40, "rows": 40, "status": {"ok": 40}},
  {"dataset": "deepset/prompt-injections", "flagged": 16, "judged": 40, "rows": 40, "status": {"ok": 40}}
]
```

The exact counts are one live run, not a claim of a stable population rate. The important observable is that both public sets are fetched by the repro and passed through the same public `webscreen.screen()` function, without local fixtures or private transcripts.

## Output of `jev doctor`

Not applicable: this is a direct `jevkit.webscreen.screen()` reproduction and does not install the plugin or invoke the `jev` CLI. The repro emits no prompt text, decision log, or API key.

## Version

Hermes Jev Skills `v0.18.0` / current repository HEAD at the time of reproduction.

## Where it runs

- Hermes
- Python 3.9+
- The Jev CLI is not required for this direct-library repro.

## OS and Python version

Any supported Python 3.9+ environment; the reported run was on macOS with the repository's standard-library-only setup.

## Why this matters

A web-result screen is used at a seam where unseen pages reach an agent. An in-distribution planted score is useful, but it does not establish recall on public attack distributions. Presenting the planted score without a separate held-out public-set result can make deployment recall look stronger than the observed cross-corpus behavior.

## Root-cause code path

At `jevkit/webscreen.py:110`, `screen()` extracts chunks and asks the shared `rerank.injection_question`; at `jevkit/webscreen.py:201`, it flags a judged unit at the fixed `INJECTION_THRESHOLD` of 0.5. The question wording comes from `jevkit/rerank.py:452`. The current scorecard and this repro therefore exercise the same broad screening path, but the scorecard's own planted attack family and these public datasets produce materially different observed catch counts. The implementation is not being accused of a crash or malformed response; the gap is that the published scorecard does not establish cross-corpus transfer.

## Workarounds exhausted

1. Re-ran the same `webscreen.screen()` path on the public S-Labs test split, selecting the first 40 `label=1` rows in source order: observed 15/40 flagged, all 40 status `ok`.
2. Ran the same path on the public deepset/prompt-injections test split, selecting the first 40 `label=1` rows in source order: observed 16/40 flagged, all 40 status `ok`.
3. Kept the model question, 0.5 threshold, local screening, and public function unchanged across both sets; no threshold was fitted on either public set.
4. Used public rows fetched at runtime rather than copied local prompt text, so the result does not depend on a private transcript or a working-machine decision log.

## Constructive ask

Keep the existing planted attack scorecard, but label it as in-distribution planted recall and add a permanently versioned public held-out attack set with its own prevalence, catch interval, clean false-positive count, and fail-open count. Keep threshold changes separately preregistered so the public set is not used for tuning.

## Out of scope

This is not a request to remove the current scorecard, declare Hermes unusable, change the 0.5 threshold, or prescribe a particular model or prompt. It asks for a separate held-out generalization measurement and clearer scope for the existing score.
