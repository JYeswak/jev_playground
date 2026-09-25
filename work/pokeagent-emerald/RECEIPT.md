# Emerald keyless state receipt

```json
{
  "image_digest": "python@sha256:da047cb8f9d1d98e5c070f5300ba9f7274e33b8fc0e5be5ed88740aed1b95ba9",
  "harness_sha": "62bf6f614b66ff76b79954e5a3f04f91c3c6a049",
  "rom_sha1": "f3ae088181bf583e55daf962a92bb46f4f1d07b7",
  "rom_mount": "read-only",
  "model_calls": 0,
  "macro_count": 372,
  "reached_controllable_overworld": true,
  "wall_time_s": 77.965,
  "state_stats": {
    "state_bytes": {
      "count": 372,
      "p50": 4677.0,
      "p95": 4692,
      "min": 1114,
      "max": 10181
    },
    "fields": {
      "visual.resolution": {
        "empty_rows": 0,
        "unique_values": 1,
        "constant": true
      },
      "visual.screenshot_present": {
        "empty_rows": 0,
        "unique_values": 1,
        "constant": true
      },
      "player.position": {
        "empty_rows": 0,
        "unique_values": 3,
        "constant": false
      },
      "player.location": {
        "empty_rows": 0,
        "unique_values": 3,
        "constant": false
      },
      "player.name": {
        "empty_rows": 0,
        "unique_values": 3,
        "constant": false
      },
      "player.party": {
        "empty_rows": 372,
        "unique_values": 1,
        "constant": true
      },
      "player.inventory": {
        "empty_rows": 372,
        "unique_values": 1,
        "constant": true
      },
      "game.game_state": {
        "empty_rows": 0,
        "unique_values": 2,
        "constant": false
      },
      "game.is_in_battle": {
        "empty_rows": 0,
        "unique_values": 1,
        "constant": true
      },
      "game.dialog_text": {
        "empty_rows": 372,
        "unique_values": 1,
        "constant": true
      },
      "game.dialogue_detected": {
        "empty_rows": 0,
        "unique_values": 1,
        "constant": true
      },
      "game.battle_info": {
        "empty_rows": 372,
        "unique_values": 1,
        "constant": true
      },
      "game.money": {
        "empty_rows": 0,
        "unique_values": 2,
        "constant": false
      },
      "game.badges": {
        "empty_rows": 372,
        "unique_values": 1,
        "constant": true
      },
      "game.time": {
        "empty_rows": 0,
        "unique_values": 1,
        "constant": true
      },
      "game.progress_context": {
        "empty_rows": 0,
        "unique_values": 2,
        "constant": false
      },
      "map.visual_map": {
        "empty_rows": 372,
        "unique_values": 1,
        "constant": true
      },
      "map.object_events": {
        "empty_rows": 228,
        "unique_values": 3,
        "constant": false
      },
      "map.stitched_map_info": {
        "empty_rows": 0,
        "unique_values": 1,
        "constant": true
      },
      "state_text": {
        "empty_rows": 0,
        "unique_values": 7,
        "constant": false
      }
    }
  },
  "position_changes": [
    {
      "macro_index": 299,
      "button": "LEFT",
      "before": {
        "x": 2,
        "y": 2
      },
      "after": {
        "x": 1,
        "y": 2
      }
    },
    {
      "macro_index": 303,
      "button": "RIGHT",
      "before": {
        "x": 1,
        "y": 2
      },
      "after": {
        "x": 2,
        "y": 2
      }
    }
  ],
  "quoted_rows": [
    {"macro_index":299,"button":"LEFT","wall_s":63.64247,"state_bytes":4691,"position":{"x":1,"y":2},"location":"MOVING_VAN","game_state":"overworld"},
    {"macro_index":303,"button":"RIGHT","wall_s":64.44204,"state_bytes":4680,"position":{"x":2,"y":2},"location":"MOVING_VAN","game_state":"overworld"}
  ],
  "scratch_screenshots": "/scratch",
  "output_jsonl": "/out/states/emerald-boot.jsonl"
}
```
