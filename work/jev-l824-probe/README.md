# OMP find Jev latency probe

This probe compares 20 sequential Jev calls with 20 calls dispatched at a maximum of 16 in
flight. It uses the committed state captured from the non-authored
`docs-mirror/typesafe/llms-full.txt` source and pins `jev-1.13.0`.

Run only after the state and probe commit exists:

```bash
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/jev-l824-probe/probe.mjs
```

The script writes `live-report.json` locally. It prints only metadata, latency, usage, failure
reasons, spend, and source hash; it never prints the state or the API key.

This is a transport/queue smoke, not a relevance, accuracy, or ranking test. The input state is
fixed before the call, and the 40 calls cost the reported input-token total at `$0.042/M`.
