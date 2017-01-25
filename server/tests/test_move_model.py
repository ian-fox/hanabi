import unittest

from hanabi.exceptions import InvalidMove
from hanabi.models import Colour, Move, MoveType

class MoveModelTestCase(unittest.TestCase):
    def test_rank_hint(self):
        move_to_create = {
            'type': 'hint',
            'rank': 5,
            'playerIndex': 2
        }

        move = Move(move_to_create, 0, 3)

        self.assertEqual(move.move_type, MoveType.HINT)
        self.assertEqual(move.hint_rank, 5)
        self.assertIsNone(move.hint_colour)
        self.assertEqual(move.hinted_player, 2)
        self.assertEqual(move.moving_player, 0)

    def test_colour_hint(self):
        move_to_create = {
            'type': 'hint',
            'colour': 'rainbow',
            'playerIndex': 2
        }

        move = Move(move_to_create, 2, 3)

        self.assertEqual(move.move_type, MoveType.HINT)
        self.assertEqual(move.hint_colour, Colour.RAINBOW)
        self.assertIsNone(move.hint_rank)
        self.assertEqual(move.hinted_player, 1)
        self.assertEqual(move.moving_player, 2)

    def test_hint_both(self):
        """Invalid if they try to hint about both number and colour"""
        move_to_create = {
            'type': 'hint',
            'rank': 5,
            'colour': 'red'
        }

        self.assertRaises(InvalidMove, lambda: Move(move_to_create, 2, 3))

    def test_play_card(self):
        move_to_create = {
            'type': 'play',
            'cardIndex': 3
        }

        move = Move(move_to_create, 2, 3)

        self.assertEqual(move.move_type, MoveType.PLAY)
        self.assertEqual(move.moving_player, 2)
        self.assertEqual(move.card_index, 3)

    def test_discard_card(self):
        move_to_create = {
            'type': 'discard',
            'cardIndex': 3
        }

        move = Move(move_to_create, 2, 3)

        self.assertEqual(move.move_type, MoveType.DISCARD)
        self.assertEqual(move.moving_player, 2)
        self.assertEqual(move.card_index, 3)
