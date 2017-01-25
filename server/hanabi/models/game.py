from random import randint
from uuid import uuid4

from flask import url_for

from hanabi import db
from hanabi.exceptions import CannotJoinGame, CannotStartGame, InvalidMove
from hanabi.models import Colour, new_deck, MoveType, Card


def rotate(array, offset):
    return array[-offset:] + array[:offset]


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)

    # Settings
    hard_mode = db.Column(db.Boolean, default=False)
    perfect_mode = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, index=True, default=False)
    chameleon_mode = db.Column(db.Boolean, default=False)

    # Game Info
    discard = db.Column(db.PickleType, default={key: [] for key in Colour})
    deck = db.Column(db.PickleType, default=[])
    hands = db.Column(db.PickleType, default=[])
    hints = db.Column(db.SmallInteger, default=8)
    inPlay = db.Column(db.PickleType, default=dict.fromkeys(list(Colour), 0))
    last_turn = db.Column(db.Boolean, default=False)
    last_player = db.Column(db.SmallInteger, nullable=True, default=None)
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
            'hands': rotate(list(map(lambda arr: list(map(lambda card: card.to_json(), arr)), self.hands)),
                            player_offset),
            'hardMode': self.hard_mode,
            'deckSize': len(self.deck),
            'turn': (self.turn + player_offset) % len(self.players),
            'started': self.started,
            'chameleonMode': self.chameleon_mode,
            'perfectMode': self.perfect_mode,
            'inPlay': self.inPlay,
            'lastTurn': self.last_turn,
            'lastPlayer': self.last_player and (self.last_player + player_offset) % len(self.players),
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
        self.deck = new_deck(self.hard_mode)
        self.turn = randint(0, len(self.players) - 1)

        num_cards = 5 if len(self.players) < 4 else 4
        for i in range(len(self.players)):
            self.hands.append([])
            for j in range(num_cards):
                self.hands[-1].append(Card(self.deck.pop()))

    def make_move(self, move):
        """Make a move or raise InvalidMove"""

        if not self.started:
            raise InvalidMove('Game not started')

        if self.turn != move.moving_player:
            raise InvalidMove('Not your turn')

        if move.move_type == MoveType.HINT:
            if self.hints == 0:
                raise InvalidMove('No hints available')

            if move.moving_player == move.hinted_player:
                raise InvalidMove('Can\'t hint yourself')

            if self.chameleon_mode and move.hint_colour == Colour.RAINBOW:
                raise InvalidMove('Can\'t hint about rainbow in a chameleon mode game')

            hintedACard = False
            for card in self.hands[move.hinted_player]:
                if card.colour == move.hint_colour:
                    card.known_colour = move.hint_colour
                    hintedACard = True
                if card.rank == move.hint_rank:
                    card.known_rank = True
                    hintedACard = True

                if self.chameleon_mode and card.colour == Colour.RAINBOW:
                    hintedACard = True
                    if card.known_colour is None:
                        card.known_colour = move.hint_colour
                    else:
                        # Making the assumption they can figure out that if a card is red and green, it's rainbow
                        card.known_colour = Colour.RAINBOW

            if not hintedACard:
                raise InvalidMove('Can\'t hint about a card that doesn\'t exist')

            self.hints -= 1

        elif move.move_type == MoveType.DISCARD:
            if self.hints == 8:
                raise InvalidMove('Can\'t discard with 8 hints')

            discarded_card = self.hands[move.moving_player].pop(move.card_index)
            self.hints += 1
            self.discard[discarded_card.colour].append(discarded_card.rank)

        else:
            played_card = self.hands[move.moving_player].pop(move.card_index)
            if self.inPlay[played_card.colour] + 1 == played_card.rank:
                self.inPlay[played_card.colour] += 1
            else:
                self.misfires -= 1
                self.discard[played_card.colour].append(played_card.rank)

        # Draw a card if necessary and able
        if move.move_type != MoveType.HINT and len(self.deck) > 0:
            self.hands[move.moving_player].append(Card(self.deck.pop()))

        # Advance the turn
        self.turn = (self.turn + 1) % len(self.players)

        # Do we need to end the game?
        if len(self.deck) == 0 and not self.perfect_mode:
            self.last_turn = True
            self.last_player = move.moving_player
