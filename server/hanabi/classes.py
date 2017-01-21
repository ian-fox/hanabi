from . import db
from hanabi.colour import Colour

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

def newDeck():
    """Return a full, shuffled deck in string form"""
    return "a deck"

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