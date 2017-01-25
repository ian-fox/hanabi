import unittest
from hanabi import create_app, db
from hanabi.models import Game


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
        g = Game(players=['id1', 'id2', 'id3', 'id4'], hands=['hand1', 'hand2', 'hand3', 'hand4'])
        db.session.add(g)
        db.session.commit()
        json_game = g.to_json(2)

        self.assertListEqual(json_game['hands'], ['hand3', 'hand4', 'hand1', 'hand2'])

    def test_start(self):
        """Starting a game should work"""
        g = Game()
        g.players = ['id1', 'id2', 'id3', 'id4']

        db.session.add(g)
        db.session.commit()

        g.start()
        db.session.flush()

        self.assertTrue(g.started)
        self.assertTrue(all(map(lambda hand: len(hand) == 4, g.hands)))
        self.assertEqual(len(g.deck), 44)

    def test_start_with_three_players(self):
        """Starting a game with three players should increase hand size"""
        g = Game()
        g.players = ['id1', 'id2', 'id3']

        db.session.add(g)
        db.session.commit()

        g.start()
        db.session.flush()

        self.assertTrue(g.started)
        self.assertTrue(all(map(lambda hand: len(hand) == 5, g.hands)))
        self.assertEqual(len(g.deck), 45)
