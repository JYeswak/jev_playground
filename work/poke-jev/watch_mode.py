#!/usr/bin/env python3
"""PokéJev challenge-only watch mode.

The dry run is keyless and talks to a local Pokémon Showdown websocket. Live mode
loads credentials from the environment, accepts challenges only from the configured
owner, and never enters the ladder.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from importlib import import_module
from pathlib import Path
from typing import Any


DEFAULT_LOCAL_WS = "ws://127.0.0.1:8000/showdown/websocket"
DEFAULT_PUBLIC_SERVER = "sim3.psim.us"
DEFAULT_AUTH_URL = "https://play.pokemonshowdown.com/action.php?"


def _showdown_id(value: str) -> str:
    """Normalize a Showdown username for exact challenge-owner comparison."""
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def accepts_challenge(challenger: str, owner: str) -> bool:
    """Return true only for the configured owner; empty owners accept nothing."""
    return bool(owner) and _showdown_id(challenger) == _showdown_id(owner)


async def dry_run(ws_url: str, timeout_s: float) -> dict[str, Any]:
    """Connect to a local Showdown server and verify the unauthenticated handshake."""
    try:
        import websockets
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("websockets is required for --dry-run") from exc

    messages: list[str] = []
    async with websockets.connect(
        ws_url, open_timeout=timeout_s, close_timeout=1
    ) as ws:
        await ws.send("|/cmd roomlist")
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            remaining = max(0.05, deadline - time.monotonic())
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            except asyncio.TimeoutError:
                break
            messages.append(str(raw))
            if any("|updateuser|" in message for message in messages) and any(
                "|challstr|" in message for message in messages
            ):
                break

    joined = "\n".join(messages)
    return {
        "connected": True,
        "server": ws_url,
        "received_updateuser": "|updateuser|" in joined,
        "received_challstr": "|challstr|" in joined,
        "owner_filter": "exact_owner_only",
        "accepted_without_owner": accepts_challenge("someone", ""),
        "message_count": len(messages),
    }


def _live_player(args: argparse.Namespace) -> int:
    """Run the existing PokéJev player in owner-filtered challenge mode."""
    username = os.environ.get("POKEJEV_SHOWDOWN_USERNAME")
    password = os.environ.get("POKEJEV_SHOWDOWN_PASSWORD")
    owner = os.environ.get("POKEJEV_OWNER_USERNAME")
    if not username or not password or not owner:
        print(
            "unconfigured: set POKEJEV_SHOWDOWN_USERNAME, "
            "POKEJEV_SHOWDOWN_PASSWORD, and POKEJEV_OWNER_USERNAME (NOT_RUN)",
            file=sys.stderr,
        )
        return 2
    if not accepts_challenge(owner, owner):
        raise RuntimeError("owner username is empty after normalization")

    try:
        account_module = import_module("poke_env.ps_client.account_configuration")
        server_module = import_module("poke_env.ps_client.server_configuration")
        player_module = import_module("player")
        account_configuration = account_module.AccountConfiguration
        server_configuration = server_module.ServerConfiguration
        pokejev_player = player_module.PokeJevPlayer
    except ImportError as exc:
        print(
            f"unconfigured: poke-env/PokéJev dependencies unavailable ({exc}) (NOT_RUN)",
            file=sys.stderr,
        )
        return 2

    server = server_configuration(
        os.environ.get("POKEJEV_SHOWDOWN_SERVER", DEFAULT_PUBLIC_SERVER),
        os.environ.get("POKEJEV_SHOWDOWN_AUTH_URL", DEFAULT_AUTH_URL),
    )
    replay_dir = Path(args.replay_dir)
    replay_dir.mkdir(parents=True, exist_ok=True)
    decision_log = Path(args.decision_log)
    decision_log.parent.mkdir(parents=True, exist_ok=True)

    async def run() -> None:
        player = pokejev_player(
            battle_format=args.format,
            account_configuration=account_configuration(username, password),
            server_configuration=server,
            save_replays=str(replay_dir),
            decision_log=str(decision_log),
        )
        # This is the only public-server path: no ladder() call exists here.
        await player.accept_challenges(owner, args.games)

    asyncio.run(run())
    print(
        json.dumps({"mode": "watch", "owner": _showdown_id(owner), "games": args.games})
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Probe a local Showdown websocket without credentials",
    )
    mode.add_argument(
        "--live", action="store_true", help="Accept owner-only public challenges"
    )
    parser.add_argument(
        "--server-url", default=DEFAULT_LOCAL_WS, help="Websocket URL used by --dry-run"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Dry-run websocket timeout in seconds",
    )
    parser.add_argument(
        "--format", default="gen9ou", help="Showdown format for live challenges"
    )
    parser.add_argument(
        "--games", type=int, default=1, help="Owner challenges to accept in live mode"
    )
    parser.add_argument(
        "--replay-dir", default="watch-replays", help="Replay output directory"
    )
    parser.add_argument(
        "--decision-log", default="watch-decisions.jsonl", help="Decision log path"
    )
    parser.add_argument(
        "--ladder", action="store_true", help="Refused: ladder is separately gated"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.ladder:
        print(
            "refused: ladder mode is not implemented in challenge-only watch mode",
            file=sys.stderr,
        )
        return 2
    if args.games < 1:
        print("error: --games must be positive", file=sys.stderr)
        return 2
    if args.dry_run:
        try:
            result = asyncio.run(dry_run(args.server_url, args.timeout))
        except Exception as exc:  # pragma: no cover - network-specific
            print(f"dry-run failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, sort_keys=True))
        return 0 if result["received_updateuser"] and result["received_challstr"] else 1
    return _live_player(args)


if __name__ == "__main__":
    raise SystemExit(main())
