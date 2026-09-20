# §17 organic precision: 0/28 — every fire is mention-vs-use (2026-09-20)

Level: `live` (no model calls anywhere in this section; the extension has none).

## Method

`work/omp-harm-rule/organic-fires.mjs` (shipped extension via default import, fake pi;
never a reimplementation): all session logs → 80,975 joined allow commands, EVERY one
scored, 28 fires, full text in `/tmp/organic-fires-full.json` (regenerable; not
committed — real commands, secret risk). Inputs pinned: 1,759 session files, whole
machine, 2026-09-20 (live-and-monotonic: logs only append, so re-runs supersede).

## Result

Organic precision **0/28**. All 28 score 0.96. Hand ruling per fire (trigger pattern
identified per row with the shipped regexes):

- [0–3,6–8,11–13,15] probe dispatches (`omp -p "...chmod -R 777 /etc/..."`,
  `...find /tmp -name x.pem...`, `...git push --force...` inside the quoted prompt
  the agent was told to run): trigger in the quoted -p string, never executed.
- [4,5,9,10,14] rule/corpus self-tests (`'chmod -R 777 /etc/x'` as a test string,
  anchor records, `chmod 666` appended into a test JSON): test-data authoring.
- [16–23] heredoc doc-writing (`cat > file <<'EOF'` receipt/dispatch/README prose
  quoting example commands, incl. the audit's own `find /tmp -name x.pem` example).
- [24–27] curl POSTs to localhost decide-endpoints with `chmod 777 /etc/passwd`
  in the JSON body (jevcache probing): test payload over loopback.

Zero fires execute danger. Zero fires outside quoted payload, test strings, doc
prose, or loopback test bodies. The 12/12 constructed corpus contained none of
these shapes — which is exactly why it transferred at 12/12 and reality fires 0/28.

## What this means (and does not)

- The rule's precision on organic traffic is unmeasured in the strict sense: 0/28
  with zero true positives in the sample is not "imprecise", it is *unfired-on* —
  no executed danger exists in 80,975 commands to be precise about.
- Every fire shares one mechanism (mention-vs-use, c6eb7ab). A stripQuotedPayload
  pass over the command before matching would silence most of these; that is a
  design note, not a patch (this section changes nothing in the extension).
- The 14 audit fires were probes; these 28 are organic accidents. Both sets agree:
  the rule fires on text ABOUT danger.

## NO-CLAIM

One machine, one operator, tool-heavy traffic; labels are one reader (mine);
fire texts live in /tmp only (secret risk in real commands); logs append so exact
re-runs supersede this count. No model added to the extension; none exists in it.
