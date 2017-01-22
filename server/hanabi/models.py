from . import db
from enum import IntEnum
from random import shuffle
from flask import url_for

class Colour(IntEnum):
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

def newDeck(hardMode=False):
    """Return a full, shuffled deck in number form"""
    deck = []
    for colour in range(5):
        for rank in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]:
            deck.append(10 * colour + rank)

    if hardMode:
        for rank in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]:
            deck.append(50 + rank)
    else:
        for rank in range(1, 6):
            deck.append(50 + rank)

    shuffle(deck)
    return deck

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)

    # Settings
    hardMode = db.Column(db.Boolean, default=False)
    perfectOrBust = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, index=True, default=False)
    rainbowIsColour = db.Column(db.Boolean, default=False)

    # Game Info
    discard = db.Column(db.PickleType, default=dict.fromkeys(list(Colour)))
    deck = db.Column(db.PickleType, default=[])
    hands = db.Column(db.PickleType, default=[])
    hints = db.Column(db.SmallInteger, default=8)
    inPlay = db.Column(db.PickleType, default=dict.fromkeys(list(Colour)))
    lastTurn = db.Column(db.Boolean, default=False)
    lastPlayer = db.Column(db.SmallInteger, nullable=True, default=None)
    misfires = db.Column(db.SmallInteger, default=3)
    players = db.Column(db.PickleType, default=[])
    started = db.Column(db.Boolean, index=True, default=False)
    turn = db.Column(db.SmallInteger, default=0)

    def __repr__(self):
        return '<Game with %r players>' % len(self.players)

    def to_json(self):
        json_game = {
            'url': url_for('api.get_specific_game', id=self.id, _external=True),
            'discard': self.discard,
            'hands': self.hands,
            'hardMode': self.hardMode,
            'deckSize': len(self.deck),
            'turn': self.turn,
            'started': self.started,
            'rainbowIsColour': self.rainbowIsColour,
            'perfectOrBust': self.perfectOrBust,
            'inPlay': self.inPlay,
            'lastTurn': self.lastTurn,
            'lastPlayer': self.lastPlayer,
            'misfires': self.misfires,
            'hints': self.hints
        }
        return json_game
