import unittest
from unittest.mock import MagicMock, patch

import streamlit as st

from api.models.country import Country
from front.app import CapitalQuizGame
from front.models.question import QuizQuestion


class TestCapitalQuizGame(unittest.TestCase):
    """Test cases for the CapitalQuizGame class."""

    def setUp(self) -> None:
        """Set up the test environment with a CapitalQuizGame instance."""
        self.game: CapitalQuizGame = CapitalQuizGame(api_host="localhost", api_port=8000)

    @patch("requests.get")
    def test_get_random_country(self, mock_get: MagicMock) -> None:
        """
        Test the get_random_country method of CapitalQuizGame.

        :param MagicMock mock_get: Mocked requests.get function
        """
        mock_response: MagicMock = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "name": "France",
                "capital": "Paris",
                "population": 67391582,
                "code": "FR",
                "area": 551695,
                "currency": "Euro",
                "language": "French",
            }
        }
        mock_get.return_value = mock_response

        country: Country = self.game.get_random_country()
        self.assertIsInstance(country, Country)
        self.assertEqual(country.name, "France")
        self.assertEqual(country.capital, "Paris")

    @patch("front.app.CapitalQuizGame.get_random_country")
    def test_generate_question(self, mock_get_random_country: MagicMock) -> None:
        """
        Test the generate_question method of CapitalQuizGame.

        :param MagicMock mock_get_random_country: Mocked get_random_country method
        """
        mock_get_random_country.side_effect = [
            Country(name="France", capital="Paris"),
            Country(name="Germany", capital="Berlin"),
            Country(name="Italy", capital="Rome"),
            Country(name="Spain", capital="Madrid"),
        ]

        question: QuizQuestion = self.game.generate_question()
        self.assertIsInstance(question, QuizQuestion)
        self.assertEqual(question.country, "France")
        self.assertEqual(question.correct_answer, "Paris")
        self.assertEqual(len(question.choices), 4)
        self.assertIn("Paris", question.choices)

    def test_check_answer(self) -> None:
        """Test the check_answer method of CapitalQuizGame."""
        st.session_state.current_quiz_question = QuizQuestion(
            country="France", correct_answer="Paris", choices=["Paris", "Berlin", "Rome", "Madrid"]
        )
        st.session_state.score = 0

        self.assertTrue(self.game.check_answer("Paris"))
        self.assertEqual(st.session_state.score, 1)

        self.assertFalse(self.game.check_answer("Berlin"))
        self.assertEqual(st.session_state.score, 1)

    def test_reset_game(self) -> None:
        """Test the reset_game method of CapitalQuizGame."""
        st.session_state.score = 5
        st.session_state.current_quiz_question = QuizQuestion(
            country="France", correct_answer="Paris", choices=["Paris", "Berlin", "Rome", "Madrid"]
        )
        st.session_state.user_answer = "Paris"
        st.session_state.answer_submitted = True

        self.game.reset_game()

        self.assertEqual(st.session_state.score, 0)
        self.assertIsNone(st.session_state.current_quiz_question)
        self.assertIsNone(st.session_state.user_answer)
        self.assertFalse(st.session_state.answer_submitted)


if __name__ == "__main__":
    unittest.main()
