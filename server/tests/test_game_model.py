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
        g = Game()
        db.session.add(g)
        db.session.commit()
        json_game = g.to_json()

        expected_keys = ['url', 'inPlay', 'started', 'discard', 'turn', 'misfires', 'perfectOrBust', 'rainbowIsColour',
                         'hints', 'hands', 'deckSize']
        self.assertEqual(sorted(json_game.keys()), sorted(expected_keys))
        self.assertTrue('api/v1/games/' in json_game['url'])
        self.assertFalse(json_game['started'])
        self.assertTrue(json_game['turn'] == 0)
        self.assertTrue(json_game['misfires'] == 3)
        self.assertTrue(json_game['hints'] == 8)
        self.assertTrue(json_game['deckSize'] == 60)