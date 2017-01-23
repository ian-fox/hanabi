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
        self.assertEqual(response.status_code, 201)
        url = response.headers.get('Location')
        self.assertTrue('/api/v1/games/' in url)

        game = Game.query.all()[0]

        # Make sure the user that created it is in the game
        user_id = response.headers.get('id')
        self.assertEqual(game.players[0], user_id)
        self.assertEqual(len(game.players), 1)

        # Make sure the game has the right ID
        game_id = url.split('/')[6]
        self.assertEqual(game.id, int(game_id))

        # Check that the game hasn't started
        self.assertFalse(game.started)

        # Check other game modes
        self.assertFalse(game.hardMode)
        self.assertTrue(game.rainbowIsColour)
        self.assertFalse(game.perfectOrBust)

    def test_new_game_with_settings(self):
        """Should be able to specify settings in query"""
        # Try to make a game that's public
        response = self.client.post(
            url_for('api.new_game'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'public': True}))
        self.assertEqual(response.status_code, 201)

        url = response.headers.get('Location')
        game_id = url.split('/')[6]
        game = Game.query.get(game_id)
        self.assertTrue(game.public)

        # Try to make a game with both variants set to true, public set to false
        response = self.client.post(
            url_for('api.new_game'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'public': False, 'rainbowIsColour': False, 'perfectOrBust': True, 'hardMode': True}))
        self.assertTrue(response.status_code == 201)

        url = response.headers.get('Location')
        game_id = url.split('/')[6]
        game = Game.query.get(game_id)
        self.assertFalse(game.public)
        self.assertTrue(game.perfectOrBust)
        self.assertFalse(game.rainbowIsColour)

    def test_join_game(self):
        """Should be able to join games"""
        # Create a new game to join
        g = Game()
        db.session.add(g)
        db.session.commit()

        response = self.client.put(url_for('api.join_game', id=g.id))
        self.assertEqual(response.status_code, 200)
        url = response.headers.get('Location')
        self.assertTrue('/api/v1/games/' in url)

        # Check that we're in the game
        user_id = response.headers.get('id')
        self.assertEqual(user_id, g.players[0])

    def test_game_capacity(self):
        """Shouldn't be able to join a game with 5 players"""
        # Create a new game
        g = Game(players=['id1', 'id2', 'id3', 'id4', 'id5'])
        db.session.add(g)
        db.session.commit()

        # Try to join
        response = self.client.put(url_for('api.join_game', id=g.id))
        self.assertEqual(response.status_code, 500)

    def test_join_started_game(self):
        """Shouldn't be able to join a game that has started (in this release)"""
        # Create a new game
        g = Game(started=True)
        db.session.add(g)
        db.session.commit()

        # Try to join
        response = self.client.put(url_for('api.join_game', id=g.id))
        self.assertEqual(response.status_code, 500)

    def test_get_all_games(self):
        """Shouldn't return private games or games that have already started"""
        # Make some games
        normal_game = Game(public=True)
        started_game = Game(started=True)
        private_game = Game(public=False)
        db.session.add_all([normal_game, started_game, private_game])
        db.session.commit()

        # Try to get the games
        response = self.client.get(url_for('api.get_games'))
        self.assertEqual(response.status_code, 200)

        # We should get one result
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response), 1)

    def test_start_game(self):
        """Admin can start the game"""
        game = Game(players=['id1', 'id2'])
        db.session.add(game)
        db.session.commit()

        response = self.client.put(url_for('api.start_game', id=1), headers={'id': 'id1'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(game.started)

    def test_start_game_not_admin(self):
        """Can't start the game if you don't authenticate as admin"""
        game = Game(players=['id1', 'id2'])
        db.session.add(game)
        db.session.commit()

        # No auth
        response = self.client.put(url_for('api.start_game', id=1))

        self.assertEqual(response.status_code, 403)
        self.assertFalse(game.started)

        # Wrong auth
        response = self.client.put(url_for('api.start_game', id=1), headers={'id': 'id2'})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(game.started)

    def test_start_started_game(self):
        """Can't start a game that's started"""
        game = Game(players=['id1', 'id2'], started=True)
        db.session.add(game)
        db.session.commit()

        response = self.client.put(url_for('api.start_game', id=1), headers={'id': 'id1'})

        self.assertEqual(response.status_code, 500)

    def test_get_unauthorized_game(self):
        """Can't GET a game you aren't in"""
        game = Game(players=['id1', 'id2'])
        db.session.add(game)
        db.session.commit()

        response = self.client.get(url_for('api.get_specific_game', id=1))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(url_for('api.get_specific_game', id=1), headers={'id': 'id3'})

        self.assertEqual(response.status_code, 403)

    def test_get_rotated_game(self):
        """If you GET a game, you are player[0]"""
        game = Game(players=['id1', 'id2', 'id3', 'id4'], hands=['hand1', 'hand2', 'hand3', 'hand4'])
        db.session.add(game)
        db.session.commit()

        response = self.client.get(url_for('api.get_specific_game', id=1), headers={'id': 'id3'})

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertListEqual(json_response['hands'], ['hand3', 'hand4', 'hand1', 'hand2'])
