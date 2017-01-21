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
