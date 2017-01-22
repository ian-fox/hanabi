from . import api
from flask import jsonify, url_for
from hanabi import db
from hanabi.models import Game
from uuid import uuid4

@api.route('/games', methods=['GET'])
def get_games():
    return Game.query.filter_by(started=False).all()

@api.route('/games/new', methods=['POST'])
def new_game():
    adminID = uuid4().hex
    newgame = Game(players=[adminID])
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

    # Can't have more than 5 players
    if len(game.players) == 5:
        return jsonify({'error': 'game is full'}), 400

    newID = uuid4().hex
    game.players.append(newID)
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_json()), 200, \
           {'Location': url_for('api.get_specific_game', id=game.id, _external=True),
            'id': newID}