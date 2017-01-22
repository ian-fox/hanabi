import unittest
from flask import url_for
from hanabi import create_app, db
from hanabi.models import Game
import json

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
        """Can make a new game with default settings"""
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

    def test_new_game_with_settings(self):
        """Should be able to specify settings in query"""
        # Try to make a game that's public
        response = self.client.post(
            url_for('api.new_game'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'public': True}))
        self.assertTrue(response.status_code == 201)

        url = response.headers.get('Location')
        gameID = url.split('/')[6]
        game = Game.query.get(gameID)
        self.assertTrue(game.public)

        # Try to make a game with both variants set to true, public set to false
        response = self.client.post(
            url_for('api.new_game'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'public': False, 'rainbowIsColour': True, 'perfectOrBust': True}))
        self.assertTrue(response.status_code == 201)

        url = response.headers.get('Location')
        gameID = url.split('/')[6]
        game = Game.query.get(gameID)
        self.assertFalse(game.public)
        self.assertTrue(game.perfectOrBust)
        self.assertTrue(game.rainbowIsColour)


    def test_join_game(self):
        """Should be able to join games"""
        # Create a new game to join
        g = Game()
        db.session.add(g)
        db.session.commit()

        response = self.client.put(url_for('api.join_game', id=g.id))
        self.assertTrue(response.status_code == 200)
        url = response.headers.get('Location')
        self.assertTrue('/api/v1/games/' in url)


        # Check that we're in the game
        userID = response.headers.get('id')
        self.assertTrue(userID == g.players[0])

    def test_game_capacity(self):
        """Shouldn't be able to join a game with 5 players"""
        # Create a new game
        g = Game(players=[1,2,3,4,5])
        db.session.add(g)
        db.session.commit()

        # Try to join
        response = self.client.put(url_for('api.join_game', id=g.id))
        self.assertTrue(response.status_code == 400)

    def test_join_started_game(self):
        """Shouldn't be able to join a game that has started (in this release)"""
        # Create a new game
        g = Game(started=True)
        db.session.add(g)
        db.session.commit()

        # Try to join
        response = self.client.put(url_for('api.join_game', id=g.id))
        self.assertTrue(response.status_code == 400)

    def test_get_all_games(self):
        "Shouldn't return private games or games that have already started"
        # Make some games
        normalGame = Game(public=True)
        startedGame = Game(started=True)
        privateGame = Game(public=False)
        db.session.add_all([normalGame, startedGame, privateGame])
        db.session.commit()

        # Try to get the games
        response = self.client.get(url_for('api.get_games'))
        self.assertTrue(response.status_code == 200)

        # We should get one result
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(json_response) == 1)