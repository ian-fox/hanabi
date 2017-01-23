import unittest
from hanabi.models import Card, Colour, newDeck

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

    def test_new_deck(self):
        """Correctly generates a deck"""
        d = newDeck()

        self.assertEqual(len(d), 60)

        # Three of each one
        for colour in range(6):
            self.assertEqual(len(list(filter(lambda x: x == 10 * colour + 1, d))), 3)

        # One of each five
        for colour in range(6):
            self.assertIn(10 * colour + 5, d)

        # Two of everything else
        for colour in range(6):
            for rank in range(2, 5):
                self.assertEqual(len(list(filter(lambda x: x == 10 * colour + rank, d))), 2)

    def test_new_hard_deck(self):
        """Correctly generates a hard deck"""
        d = newDeck(True)

        self.assertEqual(len(d), 55)

        # One of each rainbow
        for rank in range(1, 5):
            self.assertEqual(len(list(filter(lambda x: x == 50 + rank, d))), 1)