import unittest
from flask import url_for
from hanabi import create_app, db
from hanabi.models import Game

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_new_game(self):
        response = self.client.post(url_for('api.new_game'))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertTrue('/api/v1/games/' in url)

        game = Game.query.all()[0]

        # Make sure the user that created it is in the game
        userID = response.headers.get('id')
        self.assertTrue(game.players[0] == userID)
        self.assertTrue(len(game.players) == 1)

        # Make sure the game has the right ID
        gameID = url.split('/')[6]
        self.assertTrue(game.id == int(gameID))

        # Check that the game hasn't started
        self.assertFalse(game.started)