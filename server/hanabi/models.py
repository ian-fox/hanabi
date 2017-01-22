from . import db
from enum import Enum
from random import shuffle
from flask import url_for

class Colour(Enum):
    BLUE = 0
    GREEN = 1
    RED = 2
    WHITE = 3
    YELLOW = 4
    RAINBOW = 5


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

    def to_json(self):
        print(self.id)
        json_game = {
            'url': url_for('api.get_specific_game', id=self.id, _external=True),
            'discard': self.discard,
            'hands': self.hands,
            'deckSize': len(self.deck),
            'turn': self.turn,
            'started': self.started,
            'rainbowIsColour': self.rainbowIsColour,
            'perfectOrBust': self.perfectOrBust,
            'inPlay': self.inPlay,
            'misfires': self.misfires,
            'hints': self.hints
        }
        return json_game
