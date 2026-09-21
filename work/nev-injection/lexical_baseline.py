#!/usr/bin/env python3
"""B5-wide lexical baseline over jev-sec-bench committed injection results.

Reads jev-sec-bench/results/injection.json (662 samples, text+label+Jev p).
Persists pairs (id,text,label) to pairs.jsonl, then scores a WIDE keyword
baseline an honest defender would write and compares paired vs Jev@0.5.

Offline. No key. No network. Exit 0 with receipt; exit 2 if corpus unreadable.
"""

import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/Users/josh/Developer/jev/jev-sec-bench/results/injection.json"

# Wide on purpose (P1's narrow-baseline lesson): security/instruction-override
# vocabulary plus jailbreak roleplay markers. Word-boundary matched, lowercase.
KEYWORDS = [
    "ignore previous",
    "ignore all previous",
    "disregard",
    "override",
    "bypass",
    "jailbreak",
    "dan mode",
    "developer mode",
    "reveal your",
    "show me your",
    "system prompt",
    "system instruction",
    "pretend you are",
    "pretend to be",
    "roleplay",
    "role-play",
    "act as if",
    "you are now",
    "new instruction",
    "confidential",
    "do not tell",
    "don't tell",
    "keep secret",
    "exfiltrate",
    "leak",
    "prompt injection",
    "inject",
    "malicious",
    "exploit",
    "payload",
    "sudo",
    "rm -rf",
    "delete all",
    "format c:",
    "password",
    "api key",
    "apikey",
    "secret key",
    "credentials",
    "social security",
    "credit card",
    "transfer money",
    "wire transfer",
    "urgent action",
    "act immediately",
    "click the link",
    "download and run",
    "disable",
    "turn off safety",
    "no restrictions",
    "unrestricted",
    "unfiltered",
    "free of limits",
    "hypothetically",
    "thought experiment",
]
RX = re.compile("|".join(re.escape(k) for k in KEYWORDS))


def main():
    try:
        with open(SRC) as fh:
            data = json.load(fh)
        samples = data["samples"]
    except Exception as exc:
        print(f"NOT_RUN corpus unreadable: {exc}")
        return 2

    pairs_path = os.path.join(HERE, "pairs.jsonl")
    with open(pairs_path, "w") as fh:
        for i, s in enumerate(samples):
            fh.write(
                json.dumps(
                    {
                        "id": f"inj-{i:04d}",
                        "text": s["text"],
                        "label": s["label"],
                    }
                )
                + "\n"
            )

    jev_hit = lex_hit = 0
    b = c = 0  # b: jev-only correct, c: lex-only correct
    lex_fp = lex_fn = 0
    for s in samples:
        truth = bool(s["label"])
        j = (s["probability"] >= 0.5) == truth
        t = s["text"].lower()
        l = bool(RX.search(t)) == truth
        jev_hit += j
        lex_hit += l
        if j and not l:
            b += 1
        elif l and not j:
            c += 1
        if not truth and bool(RX.search(t)):
            lex_fp += 1
        if truth and not bool(RX.search(t)):
            lex_fn += 1

    n = len(samples)
    # exact two-sided McNemar via binomial on discordants
    nd = b + c
    p = 0.0
    if nd:
        k = min(b, c)
        p = sum(math.comb(nd, i) for i in range(k + 1)) / 2**nd
        p = min(1.0, 2 * p if b != c else 1.0)
    receipt = {
        "n": n,
        "labels": {
            0: sum(1 for s in samples if not s["label"]),
            1: sum(1 for s in samples if s["label"]),
        },
        "jev_acc": round(jev_hit / n, 4),
        "lex_acc": round(lex_hit / n, 4),
        "jev_only": b,
        "lex_only": c,
        "lex_fp": lex_fp,
        "lex_fn": lex_fn,
        "mcnemar_two_sided_p": round(p, 4),
        "pairs": pairs_path,
        "no_claim": (
            "offline recomputation of committed probabilities vs a "
            "keyword list; says nothing about live Jev or about "
            "non-keyword attacks"
        ),
    }
    with open(os.path.join(HERE, "lexical-receipt.json"), "w") as fh:
        json.dump(receipt, fh, indent=2)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
