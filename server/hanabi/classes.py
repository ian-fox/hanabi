from . import db
from hanabi.colour import Colour
from random import shuffle

class Hand:
    def __init__(self, player):
        self.cards = []
        self.player = player

class Card:
    def __init__(self, intRepresentation):
        self.colour = Colour(intRepresentation // 10)
        self.rank = intRepresentation % 10
        self.colourKnown = False
        self.rankKnown = False

    def toNum(self):
        return 10 * self.colour.value + self.rank

def newDeck():
    """Return a full, shuffled deck in number form"""
    deck = []
    for colour in range(6):
        for rank in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]:
            deck.append(10 * colour + rank)
    shuffle(deck)
    return deck

class Player:
    def __init__(self, hand):
        self.hand = hand

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)

    discard = db.Column(db.PickleType, default=dict.fromkeys(list(Colour)))
    deck = db.Column(db.PickleType, default=newDeck())
    hands = db.Column(db.PickleType, default=[])
    hints = db.Column(db.SmallInteger, default=8)
    inPlay = db.Column(db.PickleType, default=dict.fromkeys(list(Colour)))
    misfires = db.Column(db.SmallInteger, default=3)
    perfectOrBust = db.Column(db.Boolean, default=False)
    players = db.Column(db.PickleType, default=[])
    public = db.Column(db.Boolean, default=False)
    rainbowIsColour = db.Column(db.Boolean, default=False)
    started = db.Column(db.Boolean, index=True, default=False)
    turn = db.Column(db.SmallInteger, default=0)

    def __repr__(self):
        return '<Game %r>' % self.id