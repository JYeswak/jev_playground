# omp-jev-field

Observe-only scorer for **form fields**. Form presence (`<input>` /
`placeholder` / `label`) is a regex and is the only gate. The remainder asks
three nouls:

> Is the field label in the user's language rather than engineering jargon?
> Does the placeholder merely repeat the label instead of giving an example?
> Does the error copy tell the user how to fix the field?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-field/test/
```

## Why this one calls Jev

`omp-jev-harm` dropped Jev because four regexes beat it. This surface has no
cheap expression for the three questions. `placeholderAsLabel` is a quoted-
placeholder regex and is recorded on the row; it does not skip the call.

## Stop-condition

Cut any noul that is constant at 0.5 on the fixtures.

## Decision rows

| kind | meaning |
|---|---|
| `field_scored` | Jev answered; `probabilities` present |
| `field_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
