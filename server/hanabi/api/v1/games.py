from . import api
from hanabi import db
from hanabi.classes import *

@api.route('/games', methods=['GET'])
def get_games():
    return Game.query.filter_by(started=False).all()

@api.route('/games/new', methods=['POST'])
def new_game(opts):
    return opts