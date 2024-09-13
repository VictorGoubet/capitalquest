import os
import random
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
import streamlit as st
from dotenv import load_dotenv

from api.models.country import Country
from front.models.question import QuizQuestion

load_dotenv()


class CapitalQuizGame:
    """
    A class to manage the Capital Quiz Game using the Country Information API.
    """

    def __init__(
        self,
        api_host: str,
        api_port: int,
    ) -> None:
        """
        Initialize the CapitalQuizGame.

        :param str api_host: The host address of the API server.
        :param int api_port: The port number of the API server.
        """
        self.api_base_url = f"http://{api_host}:{api_port}/api"
        self.num_questions = 10  # Default value

    def get_random_country(self) -> Country:
        """
        Fetch a random country from the API.

        :return Country: A Country object containing the fetched country data.
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

        :return QuizQuestion: A QuizQuestion object containing the generated question data.
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

        :param str user_answer: The answer provided by the user.
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
        st.set_page_config(page_title="Capital Quest", page_icon="assets/logo.png", layout="wide")
        self.load_css()  # Load external CSS

        self.display_logo()

        if "game_state" not in st.session_state:
            self.initialize_game_state()

        if st.session_state.game_state == "start":
            self._handle_start_state()
        elif st.session_state.game_state == "playing":
            self._handle_playing_state()
        elif st.session_state.game_state == "end":
            self._handle_end_state()

    def display_logo(self) -> None:
        """
        Display the game logo.
        """
        _, col2, _ = st.columns([6, 1, 6])
        with col2:
            st.image("assets/logo.png", width=180)  # Centered logo

    def load_css(self) -> None:
        """
        Load custom CSS from an external file located in the styles folder.

        This method reads the contents of the 'main.css' file from the 'styles' folder
        adjacent to the current script and applies it to the Streamlit app.
        """
        current_dir = Path(__file__).resolve().parent
        css_path = current_dir / "styles" / "main.css"
        with css_path.open("r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def initialize_game_state(self) -> None:
        """
        Initialize the game state variables in session state.
        """
        st.session_state.game_state = "start"
        st.session_state.show_next_button = False
        st.session_state.question_number = 0
        st.session_state.answer_submitted = False
        st.session_state.result_message = None
        st.session_state.score = 0
        st.session_state.num_questions = 10  # Default value

    def _handle_start_state(self) -> None:
        """
        Handle the start state of the game.
        """
        st.write(
            "<p style='text-align: center;'>Test your knowledge of world capitals.</p>",
            unsafe_allow_html=True,
        )
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            _, inner_col, _ = st.columns([1, 2, 1])
            with inner_col:
                st.session_state.num_questions = st.slider("Number of questions", min_value=5, max_value=100, value=10)
                if st.button("Start Game", use_container_width=True):
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
        if st.session_state.question_number <= st.session_state.num_questions:
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

        st.markdown(
            f"<h3 style='text-align: center;'>Question {st.session_state.question_number}/{st.session_state.num_questions}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align: center;'>What is the capital of <b>{st.session_state.current_quiz_question.country}</b>?</p>",
            unsafe_allow_html=True,
        )

        _, col2, _ = st.columns([3, 1, 3])
        with col2:
            st.session_state.user_answer = st.radio(
                "Select the correct capital:",
                st.session_state.current_quiz_question.choices,
                key=f"q{st.session_state.question_number}",
                disabled=st.session_state.answer_submitted,
                label_visibility="collapsed",
            )

    def _process_answer(self) -> None:
        """
        Process the user's answer and update the game state.
        """
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            _, col2, _ = st.columns([1, 2, 1])
            with col2:
                submit_button = st.button(
                    "Submit Answer", disabled=st.session_state.answer_submitted, use_container_width=True
                )
                if submit_button:
                    is_correct = self.check_answer(st.session_state.user_answer)
                    self._display_result(is_correct)
                    st.session_state.answer_submitted = True
                    st.session_state.show_next_button = True
                    st.rerun()

                if st.session_state.show_next_button:
                    if st.button("Next Question", use_container_width=True):
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
        country = st.session_state.current_quiz_question.country
        correct_answer = st.session_state.current_quiz_question.correct_answer
        if is_correct:
            st.session_state.result_message = (
                f"<p style='text-align: center; color: green;'>✅ Correct! "
                f"The capital of {country} is {correct_answer}.</p>"
            )
        else:
            st.session_state.result_message = (
                f"<p style='text-align: center; color: red;'>❌ Incorrect. "
                f"The capital of {country} is {correct_answer}.</p>"
            )

    def _update_game_state(self) -> None:
        """
        Update the game state after processing an answer.
        """
        st.session_state.question_number += 1
        st.session_state.user_answer = None
        st.session_state.current_quiz_question = None

        if st.session_state.question_number > st.session_state.num_questions:
            st.session_state.game_state = "end"
            st.rerun()

    def _handle_end_state(self) -> None:
        """
        Handle the end state of the game.

        Displays the final score, accuracy, and provides a button to return to the home screen.
        """
        st.markdown("<h2 style='text-align: center;'>🎉 Quiz Completed!</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align: center; font-size: 20px;'>Your final score: <b>{st.session_state.score}/{st.session_state.num_questions}</b></p>",
            unsafe_allow_html=True,
        )
        accuracy = (st.session_state.score / st.session_state.num_questions) * 100
        st.markdown(f"<p style='text-align: center;'>Accuracy: <b>{accuracy:.2f}%</b></p>", unsafe_allow_html=True)

        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            col2.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
            if st.button("Home", use_container_width=True):
                self.reset_game()
                st.session_state.game_state = "start"
                st.session_state.show_next_button = False
                st.session_state.question_number = 0
                st.session_state.answer_submitted = False
                st.session_state.result_message = None
                st.session_state.score = 0
                st.rerun()
            col2.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """
    Main function to initialize and launch the Capital Quiz Game.
    """
    game = CapitalQuizGame(api_host=os.environ["api_host"], api_port=os.environ["api_port"])
    game.launch()


if __name__ == "__main__":
    main()
