# Jev + GrokBot 7-step validation
Date: 2026-09-19T18:15:37-06:00
Host: Joshs-Mac-Studio.local

## Step 1 — TypeSafe API key exists (off chat)
PASS — TYPESAFE_API_KEY present via Infisical (chars=108, value not printed)

## Step 2 — Secure storage (no chat paste)
PASS — documented Infisical projectId in .env.example (secure inject path, not chat paste)
Note: Grok Bot secret-request card is optional when Infisical already holds the key for Studio agents.

## Step 3 — typesafe-sdk + smoke systemOne (Choice)
SDK probe: 0.6.0 function function
Smoke: {"ok":true,"choice":"research","confidence":0.46,"latencyHint":"live"}
Step 3: PASS

## Step 4 — Usage lab present (router, config, logs)
  OK work/jev-usage-router/src/router.mjs
  OK work/jev-usage-router/src/cli.mjs
  OK work/jev-usage-router/config.json
  OK work/jev-usage-router/README.md
  log work/jev-usage-router/logs/routes-2026-09-20.jsonl
Step 4: PASS

## Step 5 — Skill jev-usage-router
PASS — lab README documents /jev-usage-router skill contract (house skill saved earlier this session)
Contract required: before browser/research/retry/extra bot → call router; honor action in active; kill switches listed
5:**Jev decides** (`local` | `research` | `browser` | `bypass`). **Grok Bot executes** (or logs in shadow). Humans keep irreversible actions.
19:| `mode: "shadow"` | default — log route, caller not bound |
20:| `mode: "active"` | caller must honor `action` |
21:| `enabled: false` | kill switch (same as `BYPASS_JEV=1`) |
26:- `BYPASS_JEV=1`
32:House skill: `/jev-usage-router` — before browser / research / retry / extra bot, call this router; in shadow, log only; in active, honor `action`.
Step 5: PASS

## Step 6 — Shadow first + kill switch + read logs
config.mode=shadow enabled=True
Shadow result: {
  "id": "536d39ca-1373-40b1-ba76-98c3c0fb0e30",
  "ts": "2026-09-20T00:15:59.125Z",
  "mode": "shadow",
  "ok": true,
  "bypassed": false,
  "action": "browser",
  "rawChoice": "browser",
  "confidence": 0.77,
  "probabilities": {
    "bypass": 0,
    "browser": 0.83,
    "local": 0.01,
    "research": 0.16
  },
  "latencyMs": 1185,
  "model": "jev-1.13.0",
  "goal": "Find flights from SEA to SFO next Friday under $200",
  "binding": "log-only"
}
shadow binding OK action= browser conf= 0.77
Kill: {
  "id": "c06ad6a3-e64a-46cf-8b26-75cc3b4997bf",
  "ts": "2026-09-20T00:15:59.192Z",
  "mode": "shadow",
  "ok": true,
  "bypassed": true,
  "reason": "BYPASS_JEV=1",
  "action": "bypass",
  "confidence": null,
  "latencyMs": 0,
  "goal": "kill-switch-check"
}
kill switch OK
Last log lines:
{"id":"9f69ec87-4642-49a5-be22-a98eff245263","ts":"2026-09-20T00:07:59.477Z","mode":"shadow","ok":true,"bypassed":false,"action":"local","rawChoice":"local","confidence":1,"probabilities":{"local":1,"browser":0,"bypass":0,"research":0},"latencyMs":710,"model":"jev-1.13.0","goal":"List files in the current directory and summarize what is there","binding":"log-only"}
{"id":"536d39ca-1373-40b1-ba76-98c3c0fb0e30","ts":"2026-09-20T00:15:59.125Z","mode":"shadow","ok":true,"bypassed":false,"action":"browser","rawChoice":"browser","confidence":0.77,"probabilities":{"bypass":0,"browser":0.83,"local":0.01,"research":0.16},"latencyMs":1185,"model":"jev-1.13.0","goal":"Find flights from SEA to SFO next Friday under $200","binding":"log-only"}
{"id":"c06ad6a3-e64a-46cf-8b26-75cc3b4997bf","ts":"2026-09-20T00:15:59.192Z","mode":"shadow","ok":true,"bypassed":true,"reason":"BYPASS_JEV=1","action":"bypass","confidence":null,"latencyMs":0,"goal":"kill-switch-check"}
Step 6: PASS

## Step 7 — Flip active; GrokBot would honor route
flipped config to active
Active result: {
  "id": "0ac90087-72b5-4cb2-b3a8-70e0ef4ae8d9",
  "ts": "2026-09-20T00:16:00.490Z",
  "mode": "active",
  "ok": true,
  "bypassed": false,
  "action": "local",
  "rawChoice": "local",
  "confidence": 1,
  "probabilities": {
    "local": 1,
    "research": 0,
    "bypass": 0,
    "browser": 0
  },
  "latencyMs": 304,
  "model": "jev-1.13.0",
  "goal": "Summarize the README in the current repo from disk",
  "binding": "caller-must-honor"
}
ACTIVE OK — action= local confidence= 1 latencyMs= 304
Honor simulation for action=local:
  EXEC local: ls README.md && wc -l README.md
README.md
     860 README.md
  HONOR PASS — local path executed without browser/research
restored config to shadow (safe default)
Step 7: PASS

## Summary
| Step | Result |
|---|---|
| 1 Key off-chat (Infisical) | PASS |
| 2 Secure storage path | PASS |
| 3 SDK + Choice smoke | PASS |
| 4 Usage lab | PASS |
| 5 Skill contract | PASS |
| 6 Shadow + kill + logs | PASS |
| 7 Active + honor | PASS |

Default left at mode=shadow after validation.
