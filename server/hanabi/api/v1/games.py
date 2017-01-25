from . import api
from flask import jsonify, url_for, request
from hanabi import db
from hanabi.models import Game
from hanabi.Exceptions import CannotJoinGame
from uuid import uuid4


def game_summary(game):
    """The all games list only needs some information, not all"""
    return {
        'url': url_for('api.get_specific_game', game_id=game.id, _external=True),
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
    admin_id = uuid4().hex
    json = request.get_json() or {}

    hard_mode = json.get('hardMode') or False
    perfect_or_bust = json.get('perfectOrBust') or False
    rainbow_is_colour = json.get('rainbowIsColour')
    if rainbow_is_colour is None:
        rainbow_is_colour = True
    public = json.get('public')

    new_game_object = Game(
        players=[admin_id],
        perfectOrBust=perfect_or_bust,
        rainbowIsColour=rainbow_is_colour,
        hardMode=hard_mode,
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

    # No point starting a game with one player, or that's already started
    if len(game.players) < 2:
        return jsonify({'error': 'cannot start game with one player'}), 500

    if game.started:
        return jsonify({'error': 'game already in progress'}), 500

    # Must be admin to start the game
    request_id = request.headers.get('id')
    if request_id != game.players[0]:
        return jsonify({'error': 'must be admin to start the game'}), 403

    # Start the game
    game.start()
    db.session.add(game)
    db.session.flush()

    return jsonify(game.to_json()), 200, \
        {'Location': url_for('api.get_specific_game', game_id=game.id, _external=True)}


@api.route('/games/<int:game_id>/action', methods=['PUT'])
def game_action(game_id):
    game = Game.query.get_or_404(game_id)

    # Check that the player is in the game
    player_id = request.headers.get('id')
    if player_id not in game.players:
        return jsonify({'error': 'id missing or not in game'}), 403

    # Check that it's their turn
    if game.turn != game.players.index(player_id):
        return jsonify({'error': 'not your turn'}), 500

    # Parse json
    json = request.get_json()
    if not json:
        return jsonify({'error': 'no move object sent'}), 400

    move_type = json.get('type')

    if move_type == 'hint':
        # hint logic goes here
        pass
    elif move_type == 'play':
        # play logic goes here
        pass
    elif move_type == 'discard':
        # discard logic goes here
        pass
    else:
        return jsonify({'error': 'missing move type'}), 400
