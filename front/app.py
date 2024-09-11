import random
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import requests
import streamlit as st
from constants import API_BASE_URL
from models.question import QuizQuestion

from api.models.country import Country


class CapitalQuizGame:
    """
    A class to manage the Capital Quiz Game using the Country Information API.
    """

    def __init__(self, api_base_url: str, num_questions: int = 5):
        self.api_base_url = api_base_url
        self.num_questions = num_questions

    def get_random_country(self) -> Country:
        """
        Fetch a random country from the API.

        :return Country: A Country object containing information about a random country.
        """
        response = requests.get(f"{self.api_base_url}/random-country")
        if response.status_code == 200:
            return Country(**response.json()["data"])
        else:
            st.error(f" ❌ Failed to fetch random country: {response.text}")
            raise ValueError("Failed to fetch random country")

    def generate_question(self) -> QuizQuestion:
        """
        Generate a question for the quiz.

        :return QuizQuestion: A QuizQuestion object containing the question details.
        """
        question_country = self.get_random_country()
        choices = [question_country.capital]
        while len(choices) < 4:
            random_country = self.get_random_country()
            if random_country.capital not in choices:
                choices.append(random_country.capital)
        random.shuffle(choices)
        return QuizQuestion(country=question_country.name, correct_answer=question_country.capital, choices=choices)

    def check_answer(self, user_answer: str) -> bool:
        """
        Check if the user's answer is correct.

        :param str user_answer: The user's selected answer.
        :return bool: True if the answer is correct, False otherwise.
        """
        if (
            st.session_state.current_quiz_question
            and user_answer == st.session_state.current_quiz_question.correct_answer
        ):
            st.session_state.score += 1
            return True
        return False

    def reset_game(self) -> None:
        """
        Reset the game state.
        """
        st.session_state.score = 0
        st.session_state.current_quiz_question = None
        st.session_state.user_answer = None
        st.session_state.answer_submitted = False

    def launch(self) -> None:
        """
        Launch and manage the game flow.
        """
        st.set_page_config(page_title="Capital Quiz Game", page_icon="🌍")
        st.title("🌍 Capital Quiz Game")

        if "game_state" not in st.session_state:
            self.initialize_game_state()

        if st.session_state.game_state == "start":
            self._handle_start_state()
        elif st.session_state.game_state == "playing":
            self._handle_playing_state()
        elif st.session_state.game_state == "end":
            self._handle_end_state()

    def initialize_game_state(self):
        """
        Initialize the game state variables in session state.
        """
        st.session_state.game_state = "start"
        st.session_state.show_next_button = False
        st.session_state.question_number = 0
        st.session_state.answer_submitted = False
        st.session_state.result_message = None
        st.session_state.score = 0

    def _handle_start_state(self) -> None:
        """
        Handle the start state of the game.
        """
        st.write("Welcome to the Capital Quiz Game! Test your knowledge of world capitals.")
        if st.button("Start Game"):
            st.session_state.game_state = "playing"
            st.session_state.current_quiz_question = self.generate_question()
            st.session_state.question_number = 1
            st.session_state.answer_submitted = False
            st.session_state.result_message = None
            st.session_state.score = 0
            st.rerun()

    def _handle_playing_state(self) -> None:
        """
        Handle the playing state of the game.
        """
        if st.session_state.question_number <= self.num_questions:
            self._display_question()
            self._process_answer()

            if st.session_state.result_message:
                st.markdown(st.session_state.result_message, unsafe_allow_html=True)
        else:
            st.session_state.game_state = "end"
            st.rerun()

    def _display_question(self) -> None:
        """
        Display the current question to the user.
        """
        if st.session_state.current_quiz_question is None:
            st.session_state.current_quiz_question = self.generate_question()

        st.subheader(f"Question {st.session_state.question_number}/{self.num_questions}")
        st.write(f"What is the capital of {st.session_state.current_quiz_question.country}?")

        st.session_state.user_answer = st.radio(
            "Select the correct capital:",
            st.session_state.current_quiz_question.choices,
            key=f"q{st.session_state.question_number}",
            disabled=st.session_state.answer_submitted,
        )

    def _process_answer(self) -> None:
        """
        Process the user's answer and update the game state.
        """
        submit_button = st.button("Submit Answer", disabled=st.session_state.answer_submitted)
        if submit_button:
            is_correct = self.check_answer(st.session_state.user_answer)
            self._display_result(is_correct)
            st.session_state.answer_submitted = True
            st.session_state.show_next_button = True
            st.rerun()

        if st.session_state.show_next_button:
            if st.button("Next Question"):
                self._update_game_state()
                st.session_state.show_next_button = False
                st.session_state.answer_submitted = False
                st.session_state.result_message = None
                st.rerun()

    def _display_result(self, is_correct: bool) -> None:
        """
        Display the result of the user's answer.

        :param bool is_correct: Whether the user's answer was correct.
        """
        if is_correct:
            st.session_state.result_message = (
                f"✅ Correct! The capital of {st.session_state.current_quiz_question.country} "
                f"is {st.session_state.current_quiz_question.correct_answer}."
            )
            st.success(st.session_state.result_message)
        else:
            st.session_state.result_message = (
                f"❌ Incorrect. The capital of {st.session_state.current_quiz_question.country} "
                f"is {st.session_state.current_quiz_question.correct_answer}."
            )
            st.error(st.session_state.result_message)

    def _update_game_state(self) -> None:
        """
        Update the game state after processing an answer.
        """
        st.session_state.question_number += 1
        st.session_state.user_answer = None
        st.session_state.current_quiz_question = None

        if st.session_state.question_number > self.num_questions:
            st.session_state.game_state = "end"
            st.rerun()

    def _handle_end_state(self) -> None:
        """
        Handle the end state of the game.
        """
        st.subheader("🎉 Quiz Completed!")
        st.write(f"Your final score: {st.session_state.score}/{self.num_questions}")
        accuracy = (st.session_state.score / self.num_questions) * 100
        st.write(f"Accuracy: {accuracy:.2f}%")

        if st.button("Home"):
            self.reset_game()
            st.session_state.game_state = "start"
            st.session_state.show_next_button = False
            st.session_state.question_number = 0
            st.session_state.answer_submitted = False
            st.session_state.result_message = None
            st.session_state.score = 0
            st.rerun()


def main() -> None:
    """
    Main function to initialize and launch the Capital Quiz Game.
    """
    game = CapitalQuizGame(api_base_url=API_BASE_URL)
    game.launch()


if __name__ == "__main__":
    main()
