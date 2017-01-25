import unittest

from hanabi import create_app, db
from hanabi.exceptions import CannotJoinGame, CannotStartGame
from hanabi.models import Card, Game


class GameModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_to_json(self):
        """Should return the relevant information"""
        g = Game(players=['id1'])
        db.session.add(g)
        db.session.commit()
        json_game = g.to_json(0)

        expected_keys = ['url', 'inPlay', 'started', 'discard', 'turn', 'misfires', 'perfectMode', 'chameleonMode',
                         'hints', 'hands', 'deckSize', 'hardMode', 'lastTurn', 'lastPlayer']
        self.assertEqual(sorted(json_game.keys()), sorted(expected_keys))
        self.assertTrue('api/v1/games/' in json_game['url'])
        self.assertFalse(json_game['started'])
        self.assertEqual(json_game['turn'], 0)
        self.assertEqual(json_game['misfires'], 3)
        self.assertEqual(json_game['hints'], 8)

    def test_to_json_different_index(self):
        """The hands should be arranged such that the specified player is index 0"""
        g = Game(players=['id1', 'id2', 'id3', 'id4'], hands=[[Card(1)], [Card(2)], [Card(3)], [Card(4)]])
        db.session.add(g)
        db.session.commit()
        json_game = g.to_json(2)

        self.assertListEqual(json_game['hands'], list(map(lambda x: [Card(x).to_json()], [3, 4, 1, 2])))

    def test_start(self):
        """Starting a game should work"""
        g = Game(players=['id1', 'id2', 'id3', 'id4'])
        db.session.add(g)
        db.session.commit()

        g.start()
        db.session.flush()

        self.assertTrue(g.started)
        self.assertTrue(all(map(lambda hand: len(hand) == 4, g.hands)))
        self.assertEqual(len(g.deck), 44)

    def test_start_with_one_player(self):
        """Can't start a game with one player"""
        g = Game(players=['id1'])
        db.session.add(g)
        db.session.commit()

        self.assertRaises(CannotStartGame, g.start)

        db.session.flush()

        self.assertFalse(g.started)

    def test_start_started_game(self):
        """Can't start a game that's already started"""
        g = Game(started=True)
        db.session.add(g)
        db.session.commit()

        self.assertRaises(CannotStartGame, g.start)

    def test_start_with_three_players(self):
        """Starting a game with three players should increase hand size"""
        g = Game(players=['id1', 'id2', 'id3'])
        db.session.add(g)
        db.session.commit()

        g.start()
        db.session.flush()

        self.assertTrue(g.started)
        self.assertTrue(all(map(lambda hand: len(hand) == 5, g.hands)))
        self.assertEqual(len(g.deck), 45)

    def test_add_player(self):
        """Add a new player to the game"""
        g = Game(players=['id1', 'id2'])
        db.session.add(g)
        db.session.commit()

        new_id = g.add_player()

        db.session.flush()

        self.assertListEqual(g.players, ['id1', 'id2', new_id])

    def test_add_player_game_started(self):
        """Can't add a player if the game is started"""
        g = Game(players=['id1', 'id2'], started=True)
        db.session.add(g)
        db.session.commit()

        self.assertRaises(CannotJoinGame, g.add_player)

        db.session.flush()
        self.assertEqual(len(g.players), 2)

    def test_add_sixth_player(self):
        """Can't add a player if the game is started"""
        g = Game(players=['id1', 'id2', 'id3', 'id4', 'id5'], started=True)
        db.session.add(g)
        db.session.commit()

        self.assertRaises(CannotJoinGame, g.add_player)

        db.session.flush()
        self.assertEqual(len(g.players), 5)

    # Making moves tested in test_game_routes.py
