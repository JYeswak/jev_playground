# jev-usage-router

Shadow-first usage router for Grok Bot + Jev.

**Jev decides** (`local` | `research` | `browser` | `bypass`). **Grok Bot executes** (or logs in shadow). Humans keep irreversible actions.

## Setup (no key in chat)

```bash
export INFISICAL_DOMAIN=https://secrets.zeststream.ai
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
  node work/jev-usage-router/src/cli.mjs --goal "Research three AI tools and draft a briefing"
```

## Config (`config.json`)

| field | meaning |
|---|---|
| `mode: "shadow"` | default — log route, caller not bound |
| `mode: "active"` | caller must honor `action` |
| `enabled: false` | kill switch (same as `BYPASS_JEV=1`) |
| `confidenceFloor` | below floor → force `bypass` |

## Kill switches

- `BYPASS_JEV=1`
- `JEV_USAGE_ROUTER=0`
- `config.enabled: false`

## Skill

House skill: `/jev-usage-router` — before browser / research / retry / extra bot, call this router; in shadow, log only; in active, honor `action`.
