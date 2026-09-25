"""Offline tests for the Stage A labeller, option sets and floors (no key, no network, no PokéChamp).

Run: cd work/poke-jev && python3 -m unittest test_replay
"""

import math
import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__))
)  # import from any cwd (CI runs from root)
import replay as r  # noqa: E402

BATTLE = """|player|p1|alice|1|1500
|player|p2|bob|2|1480
|gametype|singles
|gen|9
|poke|p1|great tusk|
|poke|p1|ogerpon-wellspring, f|
|poke|p1|kingambit, m|
|poke|p2|gholdengo|
|poke|p2|dragapult, m|
|poke|p2|urshifu-*, m|
|teampreview
|start
|switch|p1a: tusky|great tusk|100/100
|switch|p2a: gholdengo|gholdengo|100/100
|turn|1
|
|-terastallize|p1a: tusky|steel
|move|p2a: gholdengo|make it rain|p1a: tusky
|move|p1a: tusky|headlong rush|p2a: gholdengo
|-damage|p2a: gholdengo|40/100
|upkeep
|turn|2
|
|switch|p2a: pult|dragapult, m|100/100
|move|p1a: tusky|ice spinner|p2a: pult
|faint|p2a: pult
|
|switch|p2a: fish|urshifu-rapid-strike, m|100/100
|turn|3
|
|cant|p1a: tusky|par
|move|p2a: fish|surging strikes|p1a: tusky
|turn|4
|
|move|p2a: fish|surging strikes|p1a: tusky
|faint|p1a: tusky
|
|switch|p1a: kingambit|kingambit, m|100/100
|turn|5
|
|move|p1a: kingambit|outrage|p2a: fish
|move|p2a: fish|u-turn|p1a: kingambit
|switch|p2a: gholdengo|gholdengo|40/100
|turn|6
|
|move|p1a: kingambit|outrage|p2a: gholdengo|[from]lockedmove
|move|p2a: gholdengo|shadow ball|p1a: kingambit
|turn|7
|
|move|p1a: kingambit|struggle|p2a: gholdengo
|move|p2a: gholdengo|sleep talk|p2a: gholdengo
|move|p2a: gholdengo|make it rain|p1a: kingambit|[from]move: sleep talk
|
|win|alice"""


def lines():
    return r.clean_lines(BATTLE)


def block(text):
    return r.clean_lines(text)


class LabelRule(unittest.TestCase):
    def test_chosen_move_with_tera_declared_earlier_in_the_turn(self):
        b = r.turn_blocks(lines())[1]
        self.assertEqual(
            r.label(b, "p1"), {"kind": "move", "key": "headlongrush", "tera": True}
        )
        self.assertEqual(
            r.label(b, "p2"), {"kind": "move", "key": "makeitrain", "tera": False}
        )

    def test_switch_before_any_move_is_a_choice_and_keys_to_the_species(self):
        b = r.turn_blocks(lines())[2]
        self.assertEqual(
            r.label(b, "p2"),
            {"kind": "switch", "key": "dragapult", "species": "dragapult"},
        )

    def test_cant_hides_the_choice_so_the_turn_is_unobservable(self):
        self.assertIsNone(r.label(r.turn_blocks(lines())[3], "p1"))

    def test_fainting_before_acting_is_unobservable(self):
        self.assertIsNone(r.label(r.turn_blocks(lines())[4], "p1"))

    def test_switch_after_a_move_is_forced_not_chosen(self):
        b = block("|move|p2a: fish|u-turn|p1a: x\n|switch|p2a: g|gholdengo|40/100")
        self.assertEqual(
            r.label(b, "p2"), {"kind": "move", "key": "uturn", "tera": False}
        )
        b2 = block("|move|p1a: x|roar|p2a: fish\n|switch|p2a: g|gholdengo|40/100")
        self.assertIsNone(r.label(b2, "p2"))

    def test_locked_struggle_and_called_moves_are_not_choices(self):
        blocks = r.turn_blocks(lines())
        self.assertIsNone(r.label(blocks[6], "p1"))  # [from]lockedmove
        self.assertIsNone(r.label(blocks[7], "p1"))  # struggle
        self.assertEqual(
            r.label(blocks[7], "p2"),
            {"kind": "move", "key": "sleeptalk", "tera": False},
        )

    def test_drag_is_forced(self):
        self.assertIsNone(r.label(block("|drag|p1a: x|kingambit, m|100/100"), "p1"))

    def test_no_event_is_unobservable(self):
        self.assertIsNone(r.label(block("|-weather|sandstorm|[upkeep]"), "p1"))


class Snapshots(unittest.TestCase):
    def test_eligible_turns_need_both_sides_observable(self):
        turns = [e["turn"] for e in r.eligible_turns(lines(), "p1")]
        self.assertEqual(turns, [1, 2, 5])

    def test_snapshot_tracks_actives_faints_and_tera_before_the_turn(self):
        snaps = dict(r.track(lines()))
        self.assertEqual(snaps[1]["active"], {"p1": "greattusk", "p2": "gholdengo"})
        self.assertFalse(snaps[1]["tera_used"]["p1"])
        self.assertTrue(snaps[2]["tera_used"]["p1"])
        self.assertEqual(snaps[3]["active"]["p2"], "urshifu")
        self.assertEqual(snaps[3]["fainted"]["p2"], {"dragapult"})
        self.assertEqual(snaps[5]["fainted"]["p1"], {"greattusk"})

    def test_seen_moves_are_only_those_revealed_before_the_turn(self):
        snaps = dict(r.track(lines()))
        self.assertEqual(snaps[1]["seen_moves"]["p2"], {})
        self.assertEqual(snaps[2]["seen_moves"]["p2"], {"gholdengo": ["makeitrain"]})

    def test_switch_options_exclude_active_and_fainted_and_merge_formes(self):
        ln = lines()
        snaps = dict(r.track(ln))
        preview = r.team_preview(ln)
        self.assertEqual(r.switch_keys(snaps[5], "p1", preview), ["ogerpon"])
        self.assertEqual(r.switch_keys(snaps[3], "p2", preview), ["gholdengo"])

    def test_hindsight_moves_keep_locked_repeats_but_not_called_moves(self):
        hm = r.hindsight_moves(lines())
        self.assertEqual(hm["p1"]["kingambit"], ["outrage"])
        self.assertEqual(
            hm["p2"]["gholdengo"], ["makeitrain", "shadowball", "sleeptalk"]
        )

    def test_winner_and_exclusions(self):
        self.assertEqual(r.winner_side(lines()), "p1")
        self.assertIsNone(r.is_excluded(lines()))
        self.assertEqual(
            r.is_excluded(lines() + ["|switch|p2a: z|zoroark, m|100/100"]), "illusion"
        )


class OptionsAndFloors(unittest.TestCase):
    SETS = {
        "greattusk": {
            "moves": [
                {"name": "Headlong Rush", "percentage": 80.0},
                {"name": "Rapid Spin", "percentage": 19.0},
            ]
        }
    }

    def test_option_order_and_tera_variants_only_when_available(self):
        self.assertEqual(
            r.options(["a", "b"], ["x"], False), ["move a", "move b", "switch x"]
        )
        self.assertEqual(
            r.options(["a"], ["x"], True),
            ["move a", "move a + terastallize", "switch x"],
        )

    def test_option_key_matches_labels(self):
        self.assertEqual(
            r.option_key({"kind": "move", "key": "a", "tera": True}),
            "move a + terastallize",
        )
        self.assertEqual(r.option_key({"kind": "switch", "key": "x"}), "switch x")

    def test_usage_floor_is_a_distribution_weighted_by_usage(self):
        opts = r.options(["headlongrush", "rapidspin", "unknownmove"], ["x", "y"], True)
        p = r.usage_floor(opts, "greattusk", self.SETS, p_switch=0.2, p_tera=0.1)
        self.assertTrue(math.isclose(sum(p.values()), 1.0, abs_tol=1e-12))
        self.assertAlmostEqual(p["switch x"], 0.1)
        self.assertGreater(p["move headlongrush"], p["move rapidspin"])
        self.assertGreater(p["move unknownmove"], 0.0)  # +1 smoothing, never zero
        self.assertAlmostEqual(
            p["move headlongrush + terastallize"] / p["move headlongrush"], 0.1 / 0.9
        )

    def test_usage_floor_puts_all_mass_on_the_only_kind_available(self):
        p = r.usage_floor(["switch x", "switch y"], "greattusk", self.SETS, 0.2, 0.1)
        self.assertEqual(p, {"switch x": 0.5, "switch y": 0.5})
        q = r.usage_floor(["move headlongrush"], "greattusk", self.SETS, 0.2, 0.1)
        self.assertEqual(q, {"move headlongrush": 1.0})

    def test_species_key_merges_preview_and_battle_formes(self):
        self.assertEqual(
            r.species_key("urshifu-*"), r.species_key("urshifu-rapid-strike")
        )
        self.assertEqual(r.species_key("ogerpon-wellspring, f"), "ogerpon")
        self.assertNotEqual(r.species_key("chien-pao"), r.species_key("chi-yu"))


if __name__ == "__main__":
    unittest.main()
