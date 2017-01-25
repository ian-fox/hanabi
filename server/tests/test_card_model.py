import unittest

from hanabi.models import Card, Colour


class CardModelTestCase(unittest.TestCase):
    def test_conversion_from_int(self):
        """Correctly converts from integer to card"""
        c = Card(1)

        self.assertEqual(c.colour, Colour.BLUE)
        self.assertEqual(c.rank, 1)
        self.assertFalse(c.colourKnown)
        self.assertFalse(c.rankKnown)

        c = Card(42)
        self.assertEqual(c.colour, Colour.YELLOW)
        self.assertEqual(c.rank, 2)
        self.assertFalse(c.colourKnown)
        self.assertFalse(c.rankKnown)
