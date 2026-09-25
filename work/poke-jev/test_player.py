"""Offline regression tests for PokeJevPlayer option construction."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import player  # noqa: E402
from poke_env.environment import move as move_module  # noqa: E402
from poke_env.environment.move import Move  # noqa: E402


class OptionConstruction(unittest.TestCase):
    def test_ignores_showdown_placeholder_move_nothing(self):
        class FakePlayer:
            def create_order(self, move, **kwargs):
                if move.id == "nothing":
                    raise ValueError("Unknown move: nothing")
                return SimpleNamespace(message=move.id)

        with patch.object(
            move_module.GenData,
            "from_gen",
            return_value=SimpleNamespace(
                moves={"nothing": {"pp": 1}, "tackle": {"pp": 35}}
            ),
        ):
            available_moves = [Move("nothing", gen=9), Move("tackle", gen=9)]
        battle = SimpleNamespace(
            available_moves=available_moves,
            can_tera=True,
            available_switches=[],
        )

        _, orders, display = player.PokeJevPlayer._our_options(FakePlayer(), battle)

        self.assertEqual(set(orders), {"move tackle", "move tackle + terastallize"})
        self.assertEqual(set(display), {"move tackle", "move tackle + terastallize"})


if __name__ == "__main__":
    unittest.main()
