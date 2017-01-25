from enum import IntEnum
from random import shuffle

class Colour(IntEnum):
    BLUE = 0
    GREEN = 1
    RED = 2
    WHITE = 3
    YELLOW = 4
    RAINBOW = 5

class Card:
    def __init__(self, int_representation):
        self.colour = Colour(int_representation // 10)
        self.rank = int_representation % 10
        self.known_colour = None
        self.known_rank = False

    def to_num(self):
        return 10 * self.colour.value + self.rank

    def to_json(self):
        return {
            'colour': self.colour,
            'rank': self.rank,
            'knownColour': self.known_colour,
            'knownRank': self.known_rank
        }


def new_deck(hard_mode=False):
    """Return a full, shuffled deck in number form"""
    deck = []
    for colour in range(5):
        for rank in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]:
            deck.append(10 * colour + rank)

    if not hard_mode:
        for rank in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]:
            deck.append(50 + rank)
    else:
        for rank in range(1, 6):
            deck.append(50 + rank)

    shuffle(deck)
    return deck
