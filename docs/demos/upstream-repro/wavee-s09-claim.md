# §9 CLAIM STUB — SDK-surface field traps (pane 3, 2026-09-20)

Claiming this section. Verified core evidence before starting (not from the packet):

- `recording()` (`register.mjs:113-131`) files every successful `askJevChoice`
  call as `ok:false` — the choice shape `{choice, confidence, probabilities}` has
  no `scores`. `recordingChoice` (`:146+`) fixes it; test at `register.test.mjs:123`
  ("does not misfile a successful choice as a failure") is the planted negative.
  Suite: 13/13 green just now.
- `askJev` returns `{scores}`; `askJevChoice` returns `{choice, confidence,
  probabilities}`. No `.score` (singular) caller exists in jev-client.

Target: field-name trap inventory + refuse-silent-null rule + ruling on whether
`.score`'s absence is a gap or a correct refusal. Full receipt follows; this stub
is the claim only.
