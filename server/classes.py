from enum import Enum

class Colour(Enum):
    BLUE = 1
    GREEN = 2
    RED = 3
    WHITE = 4
    YELLOW = 5
    RAINBOW = 6

class Hand:
    def __init__(self, player):
        self.cards = []
        self.player = player

class Card:
    def __init__(self, colour, rank):
        self.colour = colour
        self.rank = rank
        self.colourKnown = False
        self.rankKnown = False

class Player:
    def __init__(self, hand):
        self.hand = hand
