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
        'hardMode': game.hardMode,
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
    rainbowIsColour = not (json and 'rainbowIsColour' in json.keys() and not bool(json['rainbowIsColour']))
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
    game = Game.query.get_or_404(id)

    playerID = request.headers.get('id')
    if not playerID in game.players:
        return jsonify({'error': 'id missing or not in game'}), 403

    return jsonify(game.to_json(game.players.index(playerID))), 200, \
           {'Location': url_for('api.get_specific_game', id=id, _external=True)}

@api.route('/games/<int:id>/join', methods=['PUT'])
def join_game(id):
    game = Game.query.get_or_404(id)

    # Can't have more than 5 players, can't join a game that's started already (yet)
    if len(game.players) == 5:
        return jsonify({'error': 'game is full'}), 500

    if game.started:
        return jsonify({'error': 'game has already started'}), 500

    newID = uuid4().hex
    game.players.append(newID)
    db.session.add(game)
    db.session.flush()

    return jsonify(game.to_json()), 200, \
           {'Location': url_for('api.get_specific_game', id=game.id, _external=True),
            'id': newID}

@api.route('/games/<int:id>/start', methods=['PUT'])
def start_game(id):
    game = Game.query.get_or_404(id)

    # No point starting a game with one player, or that's already started
    if len(game.players) < 2:
        return jsonify({'error': 'cannot start game with one player'}), 500

    if game.started:
        return jsonify({'error': 'game already in progress'}), 500

    # Must be admin to start the game
    requestID = request.headers.get('id')
    if (requestID != game.players[0]):
        return jsonify({'error': 'must be admin to start the game'}), 403

    # Start the game
    game.start()
    db.session.add(game)
    db.session.flush()

    return jsonify(game.to_json()), 200, \
           {'Location': url_for('api.get_specific_game', id=game.id, _external=True)}
