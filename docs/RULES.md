# Measurement rules

Eight rules, each earned by a measurement in this repo. Every one names the commit that produced
it and a command you can run now. A rule with no runnable command is not on this page.

**1. Compute the ceiling before you measure the candidate.** Give the job to an omniscient judge
first; if it cannot clear the bar, no real policy can and the candidate is irrelevant. *(`fa78767`
— omniscient saved 20.8–31.0% of bytes against a preregistered 50% bar, REJECT on 12 of 12 real
sessions, zero model calls.)*
```sh
node work/jev-retransmit-killer/ceiling-beat.mjs 2
```

**2. A savings number without a paired retention number is not a result.** "Dropped X%" is
indistinguishable from deleting everything, which drops 100%. *(`fa78767` — `drop-largest` saved
88.3%, the best figure on the page, and lost 35.8% of substantive reuse.)*
```sh
# the last two columns are drop-largest: 73.7% saved, 31.1% of substantive reuse lost
node work/jev-retransmit-killer/ceiling-beat.mjs 1 | grep REJECT
```

**3. Commit the falsifier before the first call.** Write down what result would prove you wrong,
commit it, then run. *(`beb45d5` → `61e953b`, fired and killed a question family; `8e43ccb` →
`fa78767`, did not fire and the claim stood.)*
```sh
git show --stat 8e43ccb
```

**4. Read the near-threshold count before the prevalence.** Scores clustered at the fire line mean
your threshold decided, not the model. *(`61e953b` — 197 of 400 rows within ±0.10 of 0.50,
p50 = 0.49: half the verdicts were the threshold's.)*
```sh
python3 work/toolcall-judge-v3/consequence-threshold-check.py
```

**5. Pin the input at quote time, not when someone doubts you.** Print the identity of the data
beside every number. *(`c816150` — four numbers went stale mid-session, including a corpus that
grew 77,767 → 78,242 under an already-committed receipt.)*
```sh
node --experimental-strip-types work/jev-score-register/replay.mjs \
  work/jev-score-register/fixtures/scores-pinned-20260920.jsonl
```

**6. A gate nobody has seen fail is a decoration.** Ship planted-bad inputs proving it fires, and
make each one name why the thing it guards exists. *(`fa78767` — five trees, of which the
moved-bar case matters most: lowering the bar turns REJECT into ADOPT and leaves every other check
green. `6ff34bc` — a test asserting the OLD wrapper misfiles every successful call, so nobody can
delete the fix without a red test explaining it.)*
```sh
node --test work/jev-retransmit-killer/adopt-gate.test.mjs
```

**7. A model honours the surface of a question and drops its qualifier.** Rewording does not fix
it. *(`c6eb7ab` — prose *discussing* publication scored as publication; `61e953b` — a consequence
rewrite still fired on 44.6% of its own benign falsifier set against 50.0% of everything else.)*
```sh
python3 -c "import json;f=json.load(open('work/toolcall-judge-v3/seat-consequence.json'))['falsifier'];print('falsifier fired',f['fired'],'/',f['benignTruncationRows'])"
```

**8. Store a hash of the input, never the input.** *(`6ff34bc` — the register keeps a sha256 and no
preview; the tool that kept a 200-char preview wrote credentials to a world-readable file,
[hyperspaceai/jevcache#1](https://github.com/hyperspaceai/jevcache/issues/1).)*
```sh
node --test work/jev-score-register/register.test.mjs 2>&1 | grep "not recoverable"
```
