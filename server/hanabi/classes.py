from . import db

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

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)

    discard = db.Column(db.PickleType)
    deck = db.Column(db.PickleType)
    hands = db.Column(db.PickleType)
    hints = db.Column(db.SmallInteger)
    inPlay = db.Column(db.PickleType)
    misfires = db.Column(db.SmallInteger)
    perfectOrBust = db.Column(db.Boolean)
    players = db.Column(db.PickleType)
    public = db.Column(db.Boolean)
    rainbowIsColour = db.Column(db.Boolean)
    started = db.Column(db.Boolean, index=True)
    turn = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<Game %r>' % self.id