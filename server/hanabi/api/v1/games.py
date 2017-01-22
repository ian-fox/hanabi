from . import api
from flask import jsonify, url_for, request
from hanabi import db
from hanabi.models import Game
from uuid import uuid4

def game_summary(game):
    """The all games list only needs some information, not all"""
    return {
        'url': url_for('api.get_specific_game', id=game.id, _external=True),
        'rainbowIsColour': game.rainbowIsColour,
        'perfectOrBust': game.perfectOrBust,
        'players': len(game.players)
    }
@api.route('/games', methods=['GET'])
def get_games():
    games = list(map(game_summary, Game.query.filter_by(started=False, public=True).all()))
    return jsonify(games), 200

@api.route('/games/new', methods=['POST'])
def new_game():
    adminID = uuid4().hex
    json = request.get_json()
    hardMode = json and 'hardMode' in json.keys() and bool(json['hardMode'])
    perfectOrBust = json and 'perfectOrBust' in json.keys() and bool(json['perfectOrBust'])
    rainbowIsColour = json and 'rainbowIsColour' in json.keys() and bool(json['rainbowIsColour'])
    public = json and 'public' in json.keys() and bool(json['public'])
    newgame = Game(
        players=[adminID],
        perfectOrBust=perfectOrBust,
        rainbowIsColour=rainbowIsColour,
        hardMode=hardMode,
        public=public)
    db.session.add(newgame)
    db.session.commit()
    return jsonify(newgame.to_json()), 201, \
           {'Location': url_for('api.get_specific_game', id=newgame.id, _external=True),
            'id': adminID}

@api.route('/games/<int:id>')
def get_specific_game(id):
    return jsonify(Game.query.get(id).to_json()), 200, \
           {'Location': url_for('api.get_specific_game', id=id, _external=True)}

@api.route('/games/<int:id>/join', methods=['PUT'])
def join_game(id):
    game = Game.query.get(id)

    if not game:
        return jsonify({'error': 'not found'}), 404

    # Can't have more than 5 players, can't join a game that's started already (yet)
    if len(game.players) == 5 or game.started:
        return jsonify({'error': 'game is full or has started'}), 400

    newID = uuid4().hex
    db.session.add(game)
    game.players.append(newID)
    db.session.flush()

    return jsonify(game.to_json()), 200, \
           {'Location': url_for('api.get_specific_game', id=game.id, _external=True),
            'id': newID}
