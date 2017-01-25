import json
import unittest

from flask import url_for

from hanabi import create_app, db
from hanabi.models import Game, Card, Colour


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
        self.assertFalse(game.hard_mode)
        self.assertFalse(game.chameleon_mode)
        self.assertFalse(game.perfect_mode)

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
            data=json.dumps({'public': False, 'chameleonMode': False, 'perfectMode': True, 'hardMode': True}))
        self.assertTrue(response.status_code == 201)

        url = response.headers.get('Location')
        game_id = url.split('/')[6]
        game = Game.query.get(game_id)
        self.assertFalse(game.public)
        self.assertTrue(game.perfect_mode)
        self.assertFalse(game.chameleon_mode)

    def test_join_game(self):
        """Should be able to join games"""
        # Create a new game to join
        g = Game()
        db.session.add(g)
        db.session.commit()

        response = self.client.put(url_for('api.join_game', game_id=g.id))
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
        response = self.client.put(url_for('api.join_game', game_id=g.id))
        self.assertEqual(response.status_code, 500)

    def test_join_started_game(self):
        """Shouldn't be able to join a game that has started (in this release)"""
        # Create a new game
        g = Game(started=True)
        db.session.add(g)
        db.session.commit()

        # Try to join
        response = self.client.put(url_for('api.join_game', game_id=g.id))
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

        response = self.client.put(url_for('api.start_game', game_id=1), headers={'id': 'id1'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(game.started)

    def test_start_game_not_admin(self):
        """Can't start the game if you don't authenticate as admin"""
        game = Game(players=['id1', 'id2'])
        db.session.add(game)
        db.session.commit()

        # No auth
        response = self.client.put(url_for('api.start_game', game_id=1))

        self.assertEqual(response.status_code, 403)
        self.assertFalse(game.started)

        # Wrong auth
        response = self.client.put(url_for('api.start_game', game_id=1), headers={'id': 'id2'})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(game.started)

    def test_start_started_game(self):
        """Can't start a game that's started"""
        game = Game(players=['id1', 'id2'], started=True)
        db.session.add(game)
        db.session.commit()

        response = self.client.put(url_for('api.start_game', game_id=1), headers={'id': 'id1'})

        self.assertEqual(response.status_code, 500)

    def test_get_unauthorized_game(self):
        """Can't GET a game you aren't in"""
        game = Game(players=['id1', 'id2'])
        db.session.add(game)
        db.session.commit()

        response = self.client.get(url_for('api.get_specific_game', game_id=1))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(url_for('api.get_specific_game', game_id=1), headers={'id': 'id3'})

        self.assertEqual(response.status_code, 403)

    def test_get_rotated_game(self):
        """If you GET a game, you are player[0]"""
        game = Game(players=['id1', 'id2', 'id3', 'id4'], hands=[[Card(1)], [Card(2)], [Card(3)], [Card(4)]], turn=2)
        db.session.add(game)
        db.session.commit()

        response = self.client.get(url_for('api.get_specific_game', game_id=1), headers={'id': 'id3'})

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertListEqual(json_response['hands'], list(map(lambda card: [card.to_json()],
                                                              [Card(3), Card(4), Card(1), Card(2)])))
        self.assertEqual(json_response['turn'], 0)

    def test_make_valid_moves(self):
        """Make some valid moves, see that they're valid"""
        game = Game(players=['id1', 'id2'], started=True, turn=0,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],         # Blue 1, 2
                           [Card(51), Card(42)]])            # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 hints player 2 about rainbow
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'rainbow', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertEqual(game.hands[1][0].known_colour, Colour.RAINBOW)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.hints, 7)
        self.assertEqual(game.turn, 1)

        # Player 2 hints player 1 about ones
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id2'},
            data=json.dumps({'type': 'hint', 'rank': 1, 'playerIndex': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(game.hands[0][0].known_rank)
        self.assertFalse(game.hands[0][1].known_rank)
        self.assertIsNone(game.hands[0][0].known_colour)
        self.assertIsNone(game.hands[0][1].known_colour)
        self.assertEqual(game.hints, 6)
        self.assertEqual(game.turn, 0)

        # Player 1 plays the one
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'play', 'cardIndex': 0}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(game.misfires, 3)
        self.assertEqual(game.inPlay[Colour.BLUE], 1)
        self.assertEqual(len(game.deck), 4)
        self.assertListEqual(list(map(lambda card: card.to_num(), game.hands[0])), [2, 1])  # Picked up another blue 1
        self.assertEqual(game.turn, 1)

        # Player 2 tries to play the two
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id2'},
            data=json.dumps({'type': 'play', 'cardIndex': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(game.misfires, 2)
        self.assertEqual(game.inPlay[Colour.YELLOW], 0)
        self.assertListEqual(game.discard[Colour.YELLOW], [2])
        self.assertEqual(len(game.deck), 3)
        self.assertListEqual(list(map(lambda card: card.to_num(), game.hands[1])), [51, 2])  # Picked up a blue 2

        # Player 1 discards the 1 they picked up
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'discard', 'cardIndex': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(game.hints, 7)
        self.assertListEqual(game.discard[Colour.BLUE], [1])
        self.assertEqual(len(game.deck), 2)
        self.assertListEqual(list(map(lambda card: card.to_num(), game.hands[0])), [2, 3])  # Picked up a blue 3

    def test_hint_with_no_hints(self):
        """Try to hint when there are none"""
        game = Game(players=['id1', 'id2'], started=True, turn=0, hints=0,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],         # Blue 1, 2
                           [Card(51), Card(42)]])            # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to hint player 2
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'rainbow', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 500)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertIsNone(game.hands[1][0].known_colour)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.hints, 0)
        self.assertEqual(game.turn, 0)

    def test_discard_with_eight_hints(self):
        """Try to discard with eight hints"""
        game = Game(players=['id1', 'id2'], started=True, turn=0, hints=8,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],  # Blue 1, 2
                           [Card(51), Card(42)]])  # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to discard
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'discard', 'cardIndex': 0}))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(game.hands[0][0].rank, 1)
        self.assertEqual(game.hands[0][1].rank, 2)
        self.assertEqual(game.hints, 8)
        self.assertEqual(game.turn, 0)

    def test_bad_hints(self):
        """Try to hint about both colour and rank, hint that does'nt match any cards, and hint with no hint"""
        game = Game(players=['id1', 'id2'], started=True, turn=0, hints=8,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],  # Blue 1, 2
                           [Card(51), Card(42)]])  # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to hint about two things
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'rainbow', 'rank': 2, 'playerIndex': 1}))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(game.hints, 8)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertIsNone(game.hands[1][0].known_colour)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.turn, 0)

        # Player 1 tries to hint about a card that isn't there
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'green', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(game.hints, 8)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertIsNone(game.hands[1][0].known_colour)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.turn, 0)

        # Player 1 tries to hint about nothing
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(game.hints, 8)
        self.assertEqual(game.turn, 0)

    def test_move_not_your_turn(self):
        """Try to do something when it isn't your turn"""
        game = Game(players=['id1', 'id2'], started=True, turn=0, hints=8,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],  # Blue 1, 2
                           [Card(51), Card(42)]])  # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to hint about two things
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id2'},
            data=json.dumps({'type': 'hint', 'colour': 'rainbow', 'rank': 2, 'playerIndex': 1}))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(game.hints, 8)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertIsNone(game.hands[1][0].known_colour)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.turn, 0)

    def test_play_with_no_index(self):
        """Try to play a card but don't say which"""
        game = Game(players=['id1', 'id2'], started=True, turn=0, hints=8,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],  # Blue 1, 2
                           [Card(51), Card(42)]])  # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to discard
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'play'}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(game.hands[0][0].rank, 1)
        self.assertEqual(game.hands[0][1].rank, 2)
        self.assertEqual(game.hints, 8)
        self.assertEqual(game.turn, 0)

    def test_move_with_no_move(self):
        """Try to do something but don't say what"""
        game = Game(players=['id1', 'id2'], started=True, turn=0)
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to discard
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(game.turn, 0)

    def test_chameleon_mode(self):
        """Can't hint about rainbow, hinting about a colour tells about rainbow"""
        game = Game(players=['id1', 'id2'], started=True, turn=0, hints=8, chameleon_mode=True,
                    deck=[5, 4, 3, 2, 1],  # Blue 1 through 5
                    hands=[[Card(1), Card(2)],  # Blue 1, 2
                           [Card(51), Card(42)]])  # Rainbow 1, Yellow 2
        db.session.add(game)
        db.session.commit()

        # Player 1 tries to hint about a rainbow card
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'rainbow', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(game.hints, 8)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertIsNone(game.hands[1][0].known_colour)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.turn, 0)

        # Player one hints about blue
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'blue', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(game.hints, 7)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertEqual(game.hands[1][0].known_colour, Colour.BLUE)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.turn, 1)

        game.turn = 0
        db.session.flush()

        # Player one hints about green
        response = self.client.put(
            url_for('api.make_move', game_id=1),
            headers={'Content-Type': 'application/json', 'id': 'id1'},
            data=json.dumps({'type': 'hint', 'colour': 'green', 'playerIndex': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(game.hints, 6)
        self.assertFalse(game.hands[1][0].known_rank)
        self.assertFalse(game.hands[1][1].known_rank)
        self.assertEqual(game.hands[1][0].known_colour, Colour.RAINBOW)
        self.assertIsNone(game.hands[1][1].known_colour)
        self.assertEqual(game.turn, 1)
