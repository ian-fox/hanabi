from enum import IntEnum

from hanabi.exceptions import InvalidMove
from hanabi.models import Colour


class MoveType(IntEnum):
    HINT = 0
    PLAY = 1
    DISCARD = 2


class HintType(IntEnum):
    COLOUR = 0
    RANK = 1


class Move:
    def __init__(self, json, player, num_players):
        self.move_type = MoveType(['hint', 'play', 'discard'].index(json['type']))
        self.moving_player = player

        if self.move_type == MoveType.HINT:
            if json.get('rank') and json.get('colour'):
                raise InvalidMove('Both rank and colour specified in hint')

            if json.get('rank'):
                self.hint_type = HintType.RANK
                self.hint_rank = json['rank']
                self.hint_colour = None
            else:
                self.hint_type = HintType.COLOUR
                self.hint_colour = Colour(['blue', 'green', 'red', 'white', 'yellow', 'rainbow'].index(json['colour']))
                self.hint_rank = None

            self.hinted_player = (json['playerIndex'] + player) % num_players

        else:
            self.card_index = json['cardIndex']
