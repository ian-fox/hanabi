from . import api

from uuid import uuid4

from flask import jsonify, url_for, request

from hanabi import db
from hanabi.exceptions import CannotJoinGame, CannotStartGame, InvalidMove
from hanabi.models import Game, Move


def game_summary(game):
    """The all games list only needs some information, not all"""
    return {
        'url': url_for('api.get_specific_game', game_id=game.id, _external=True),
        'chameleonMode': game.chameleon_mode,
        'perfectMode': game.perfect_mode,
        'hardMode': game.hard_mode,
        'players': len(game.players)
    }


@api.route('/games', methods=['GET'])
def get_games():
    games = list(map(game_summary, Game.query.filter_by(started=False, public=True).all()))
    return jsonify(games), 200


@api.route('/games/new', methods=['POST'])
def new_game():
    admin_id = uuid4().hex
    json = request.get_json() or {}

    hard_mode = json.get('hardMode') or False
    perfect_mode = json.get('perfectMode') or False
    chameleon_mode = json.get('chameleonMode') or False
    public = json.get('public')

    new_game_object = Game(
        players=[admin_id],
        perfect_mode=perfect_mode,
        chameleon_mode=chameleon_mode,
        hard_mode=hard_mode,
        public=public)

    db.session.add(new_game_object)
    db.session.commit()

    return jsonify(new_game_object.to_json()), 201, \
        {'Location': url_for('api.get_specific_game', game_id=new_game_object.id, _external=True),
            'id': admin_id}


@api.route('/games/<int:game_id>')
def get_specific_game(game_id):
    game = Game.query.get_or_404(game_id)

    player_id = request.headers.get('id')
    if player_id not in game.players:
        return jsonify({'error': 'id missing or not in game'}), 403

    return jsonify(game.to_json(game.players.index(player_id))), 200, \
        {'Location': url_for('api.get_specific_game', game_id=game_id, _external=True)}


@api.route('/games/<int:game_id>/join', methods=['PUT'])
def join_game(game_id):
    game = Game.query.get_or_404(game_id)

    try:
        new_id = game.add_player()
        db.session.add(game)
        db.session.flush()

        return jsonify(game.to_json()), 200, \
            {'Location': url_for('api.get_specific_game', game_id=game.id, _external=True),
                'id': new_id}
    except CannotJoinGame as c:
        return jsonify({'error': str(c)}), 500


@api.route('/games/<int:game_id>/start', methods=['PUT'])
def start_game(game_id):
    game = Game.query.get_or_404(game_id)

    # Must be admin to start the game
    request_id = request.headers.get('id')
    if request_id != game.players[0]:
        return jsonify({'error': 'must be admin to start the game'}), 403

    try:
        # Start the game
        game.start()
        db.session.add(game)
        db.session.flush()

        return jsonify(game.to_json()), 200, \
            {'Location': url_for('api.get_specific_game', game_id=game.id, _external=True)}
    except CannotStartGame as c:
        return jsonify({'error': str(c)}), 500


@api.route('/games/<int:game_id>/action', methods=['PUT'])
def game_action(game_id):
    game = Game.query.get_or_404(game_id)

    # Check that the player is in the game
    player_id = request.headers.get('id')
    if player_id not in game.players:
        return jsonify({'error': 'id missing or not in game'}), 403

    player = game.players.index(player_id)
    num_players = len(game.players)

    # Parse json
    json = request.get_json()

    # Make sure the json looks like we're expecting
    try:
        move = Move(json, player, num_players)
    except InvalidMove as i:
        return jsonify({'error': str(i)}), 500
    except:
        return jsonify({'error': 'Badly formed request'}), 400

    try:
        game.make_move(move)
        db.session.add(game)
        db.session.flush()

        return jsonify(game.to_json()), 200, \
            {'Location': url_for('api.get_specific_game', game_id=game.id, _external=True)}
    except InvalidMove as i:
        return jsonify({'error': str(i)}), 500
