from hanabi import db
from enum import IntEnum
from random import shuffle, randint
from flask import url_for
from hanabi.Exceptions import CannotJoinGame, CannotStartGame
from uuid import uuid4


def rotate(array, offset):
    return array[-offset:] + array[:offset]


class Colour(IntEnum):
    BLUE = 0
    GREEN = 1
    RED = 2
    WHITE = 3
    YELLOW = 4
    RAINBOW = 5


class MoveType(IntEnum):
    HINT = 0
    PLAY = 1
    DISCARD = 2


class HintType(IntEnum):
    COLOUR = 0
    RANK = 1


class Card:
    def __init__(self, int_representation):
        self.colour = Colour(int_representation // 10)
        self.rank = int_representation % 10
        self.colourKnown = False
        self.rankKnown = False

    def to_num(self):
        return 10 * self.colour.value + self.rank


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
        return '<Game %r>' % self.id

    def add_player(self):
        """Add a new player to the game and return their ID"""

        # Can't have more than 5 players, can't join a game that's started already (yet)
        if len(self.players) == 5:
            raise CannotJoinGame("Game at capacity")

        if self.started:
            raise CannotJoinGame("Game already in progress")

        new_id = uuid4().hex
        self.players.append(new_id)

        return new_id

    def to_json(self, player_offset=0):
        json_game = {
            'url': url_for('api.get_specific_game', game_id=self.id, _external=True),
            'discard': self.discard,
            'hands': rotate(self.hands, player_offset),
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

    def start(self):
        # No point starting a game with one player, or that's already started
        if len(self.players) < 2:
            raise CannotStartGame('Cannot start game with one player')

        if self.started:
            raise CannotStartGame('Game already in progress')

        self.started = True
        self.deck = new_deck(self.hardMode)
        self.turn = randint(0, len(self.players) - 1)

        num_cards = 5 if len(self.players) < 4 else 4
        for i in range(len(self.players)):
            self.hands.append([])
            for j in range(num_cards):
                self.hands[-1].append(self.deck.pop())

    def hint(self, player, type, attribute):
        self.hints -= 1
        for card in self.hands[self.player]:
            if card.colour == attribute and type == HintType.COLOUR:
                card.colourKnown = True

    def play_or_discard(self, player, index, type):
        pass
