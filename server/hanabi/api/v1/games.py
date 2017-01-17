from flask import jsonify

from . import api

@api.route('/games', methods=['GET'])
def get_games():
    return jsonify({'test': 'ing'})