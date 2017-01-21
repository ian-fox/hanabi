from . import api
from flask import jsonify, url_for
from hanabi import db
from hanabi.classes import Game

@api.route('/games', methods=['GET'])
def get_games():
    return Game.query.filter_by(started=False).all()

@api.route('/games/new', methods=['POST'])
def new_game(): #TODO: Return a uuid to make the user the game's admin
    newgame = Game()
    db.session.add(newgame)
    db.session.commit()
    return jsonify(newgame.to_json()), 201, \
           {'Location': url_for('api.get_specific_game', id=newgame.id, _external=True)}

@api.route('/games/<int:id>')
def get_specific_game(id):
    return jsonify(Game.query.get(id).to_json()), 200, \
           {'Location': url_for('api.get_specific_game', id=id, _external=True)}