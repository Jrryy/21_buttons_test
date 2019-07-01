from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from game.choices import RED, ORANGE, PURPLE, GREEN, BLUE, YELLOW, GUESS_PEG_COLOURS
from game.models import Game, Guess
from game.utils import create_new_game


class GameModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpassword')

    def test_game(self):
        """Test the Game model"""
        game = Game.objects.create(player=self.user)

        self.assertFalse(game.finished)
        self.assertEqual(game.guesses_count, 0)
        self.assertEqual(game.guesses.count(), 0)
        self.assertEqual(
            str(game),
            f"{self.user.username}'s game ({game.updated.strftime(settings.DATETIME_FORMAT)}), "
            f"unfinished."
        )

        game.finished = True
        game.save()
        game.refresh_from_db()

        self.assertEqual(
            str(game),
            f"{self.user.username}'s game ({game.updated.strftime(settings.DATETIME_FORMAT)}), "
            f"finished."
        )


class GuessModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('testuser', password='testpassword')
        self.user2 = User.objects.create_user('testuser2', password='testpassword2')

    def test_wrong_guesses(self):
        """Test incorrectly created Guesss"""
        game = Game.objects.create(player=self.user1)

        with self.assertRaisesMessage(
                ValidationError,
                'This guess has an incorrect number of pegs. Please select 4.'):
            Guess.objects.create(game=game, guess=[BLUE], is_solution=True)

        with self.assertRaisesMessage(
                ValidationError,
                'This guess has an incorrect number of pegs. Please select 4.'):
            Guess.objects.create(
                game=game,
                guess=[BLUE, YELLOW, PURPLE, ORANGE, GREEN],
                is_solution=True
            )

        Guess.objects.create(game=game, guess=[RED, RED, RED, RED], is_solution=True)

        with self.assertRaisesMessage(ValidationError, 'This game already has a solution'):
            Guess.objects.create(game=game, guess=[BLUE, BLUE, BLUE, BLUE], is_solution=True)

    def test_only_solution(self):
        """Test only a solution Guess in a Game"""
        game = Game.objects.create(player=self.user1)

        solution_guess = Guess.objects.create(
            game=game,
            guess=[ORANGE, PURPLE, YELLOW, BLUE],
            is_solution=True
        )

        self.assertTrue(solution_guess.is_solution)
        self.assertEqual(solution_guess.game, game)
        self.assertEqual(solution_guess.guess, [ORANGE, PURPLE, YELLOW, BLUE])
        self.assertIsNone(solution_guess.result_blacks)
        self.assertIsNone(solution_guess.result_whites)

        self.assertEqual(game.guesses.count(), 1)
        self.assertTrue(game.guesses.get().is_solution)
        self.assertEqual(game.guesses.get().guess, [ORANGE, PURPLE, YELLOW, BLUE])

        self.assertEqual(
            str(solution_guess),
            f"Solution for {game}\n['Orange', 'Purple', 'Yellow', 'Blue']"
        )

    def test_different_guesses(self):
        """Test a solution and a guess in the same game"""

        game = Game.objects.create(player=self.user1)

        Guess.objects.create(game=game, guess=[ORANGE, PURPLE, YELLOW, BLUE], is_solution=True)

        guess = Guess.objects.create(game=game, guess=[RED, PURPLE, BLUE, YELLOW], is_solution=False)

        self.assertFalse(guess.is_solution)
        self.assertEqual(guess.game, game)
        self.assertEqual(guess.guess, [RED, PURPLE, BLUE, YELLOW])
        self.assertEqual(guess.result_blacks, 1)
        self.assertEqual(guess.result_whites, 2)

        self.assertEqual(game.guesses.count(), 2)
        self.assertEqual(game.guesses.filter(is_solution=False).count(), 1)
        self.assertEqual(game.guesses.get(is_solution=False).guess, [RED, PURPLE, BLUE, YELLOW])

        self.assertEqual(
            str(guess),
            f"Guess in {game}\n['Red', 'Purple', 'Blue', 'Yellow'], 2 whites, 1 blacks"
        )


class UtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpassword')

    def test_create_new_game(self):
        """Test the utils function that creates a new game with a solution"""
        create_new_game(self.user)

        self.assertEqual(Game.objects.count(), 1)

        game = Game.objects.get()

        self.assertEqual(game.player, self.user)
        self.assertEqual(game.guesses_count, 0)
        self.assertEqual(game.guesses.count(), 1)

        guess = game.guesses.get()

        self.assertTrue(guess.is_solution)
        self.assertEqual(len(guess.guess), 4)
        self.assertIsNone(guess.result_whites)
        self.assertIsNone(guess.result_blacks)


class GameAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpassword')
        self.token = Token.objects.get().key
        self.user2 = User.objects.create_user('testuser2', password='anotherpassword')
        self.token2 = Token.objects.get(user=self.user2).key

    def test_create_new_game(self):
        """Test the endpoint to create new games"""
        url = reverse('new-game')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'New game created.')

        self.assertEqual(Game.objects.count(), 1)

        game = Game.objects.get()

        self.assertFalse(game.finished)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'New game created.')

        self.assertEqual(Game.objects.count(), 2)

        game.refresh_from_db()

        self.assertTrue(game.finished)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'New game created.')

        self.assertEqual(Game.objects.count(), 3)
        self.assertEqual(self.user2.games.count(), 1)

    def test_check_game_historic(self):
        """Test the endpoint to retrieve the games historic"""
        historic_url = reverse('view-historic')
        new_game_url = reverse('new-game')

        response = self.client.get(historic_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        response = self.client.get(historic_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        self.client.post(new_game_url)
        response = self.client.get(historic_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['guesses_count'], 0)
        self.assertFalse(response.data[0]['finished'])

        self.client.post(new_game_url)

        game = Game.objects.get(finished=False)
        Guess.objects.create(game=game, guess=[RED, GREEN, BLUE, YELLOW])
        # This is just in case the test actually matches the solution and the game becomes finished
        game.refresh_from_db()

        response = self.client.get(historic_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['guesses_count'], 1)
        self.assertEqual(response.data[0]['finished'], game.finished)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')

        response = self.client.get(historic_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_make_guess(self):
        """Test the endpoint to make a guess in a game"""
        make_guess_url = reverse('make-guess')

        game = Game.objects.create(player=self.user)
        guess = Guess.objects.create(game=game, guess=[RED, BLUE, YELLOW, GREEN], is_solution=True)

        response = self.client.post(make_guess_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')

        response = self.client.post(make_guess_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'You have no started games yet.')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        json = {
            'guess': [RED, BLUE]
        }

        response = self.client.post(make_guess_url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['guess'][0], 'This field must have 4 elements.')

        json = {
            'guess': [RED, BLUE, RED, YELLOW, GREEN]
        }

        response = self.client.post(make_guess_url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['guess'][0], 'This field must have 4 elements.')

        json = {
            'guess': [ORANGE, PURPLE, PURPLE, ORANGE]
        }

        response = self.client.post(make_guess_url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guess'], [ORANGE, PURPLE, PURPLE, ORANGE])
        self.assertEqual(response.data['result_whites'], 0)
        self.assertEqual(response.data['result_blacks'], 0)
        self.assertNotIn('message', response.data)

        json = {
            'guess': [BLUE, RED, PURPLE, ORANGE]
        }

        response = self.client.post(make_guess_url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guess'], [BLUE, RED, PURPLE, ORANGE])
        self.assertEqual(response.data['result_whites'], 2)
        self.assertEqual(response.data['result_blacks'], 0)
        self.assertNotIn('message', response.data)

        json = {
            'guess': [RED, BLUE, GREEN, YELLOW]
        }

        response = self.client.post(make_guess_url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guess'], [RED, BLUE, GREEN, YELLOW])
        self.assertEqual(response.data['result_whites'], 2)
        self.assertEqual(response.data['result_blacks'], 2)
        self.assertNotIn('message', response.data)

        json = {
            'guess': [RED, BLUE, YELLOW, GREEN]
        }

        response = self.client.post(make_guess_url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guess'], [RED, BLUE, YELLOW, GREEN])
        self.assertEqual(response.data['result_whites'], 0)
        self.assertEqual(response.data['result_blacks'], 4)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'You win!')

        response = self.client.post(make_guess_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'You have no started games yet.')

    def test_list_game_guesses(self):
        """Test endpoint to retrieve the list of the guesses made in the current game"""
        guesses_url = reverse('list-guess')

        game = Game.objects.create(player=self.user)
        Guess.objects.create(game=game, guess=[RED, BLUE, YELLOW, GREEN], is_solution=True)

        response = self.client.get(guesses_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')

        response = self.client.get(guesses_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'You have no started games yet.')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        response = self.client.get(guesses_url)

        self.assertEqual(response.data, [])

        Guess.objects.create(game=game, guess=[RED, ORANGE, BLUE, PURPLE])
        Guess.objects.create(game=game, guess=[RED, BLUE, YELLOW, RED])

        response = self.client.get(guesses_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.assertEqual(response.data[1]['guess'], [RED, ORANGE, BLUE, PURPLE])
        self.assertEqual(response.data[1]['result_whites'], 1)
        self.assertEqual(response.data[1]['result_blacks'], 1)

        self.assertEqual(response.data[0]['guess'], [RED, BLUE, YELLOW, RED])
        self.assertEqual(response.data[0]['result_whites'], 0)
        self.assertEqual(response.data[0]['result_blacks'], 3)

    def test_list_peg_colours(self):
        """Test endpoint to receive the possible peg colours to choose from"""
        colours_url = reverse('list-colours')

        response = self.client.get(colours_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        response = self.client.get(colours_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, GUESS_PEG_COLOURS)
