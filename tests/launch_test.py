import os
import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from launch import (
    run_api,
    run_front,
    set_environment_variables,
    set_log_level,
    setup_signal_handlers,
    start_components,
    wait_for_processes,
)


class TestLaunchScript(unittest.TestCase):
    """Test cases for the launch script."""

    def setUp(self) -> None:
        """
        Set up the test environment with default environment variables.
        """
        self.env_vars: Dict[str, str] = {
            "api_host": "localhost",
            "api_port": "8000",
            "front_host": "localhost",
            "front_port": "8051",
            "environment": "dev",
        }

    def test_set_log_level(self) -> None:
        """
        Test the set_log_level function for both dev and prod environments.
        """
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            set_log_level("dev")
            mock_logger.setLevel.assert_called_with(10)  # DEBUG level

            set_log_level("prod")
            mock_logger.setLevel.assert_called_with(20)  # INFO level

    def test_set_environment_variables(self) -> None:
        """
        Test the set_environment_variables function with default values.
        """
        with patch.dict(os.environ, {}, clear=True):
            set_environment_variables(None, None, None, None, None)
            for key, value in self.env_vars.items():
                self.assertEqual(os.environ.get(key), value)

    @patch("launch.Process")
    def test_start_components(self, mock_process: MagicMock) -> None:
        """
        Test the start_components function for different component configurations.

        :param MagicMock mock_process: Mocked Process class
        """
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance

        processes: List[Any] = start_components("both")
        self.assertEqual(len(processes), 2)
        mock_process_instance.start.assert_called()

        processes = start_components("api")
        self.assertEqual(len(processes), 1)
        mock_process_instance.start.assert_called()

        processes = start_components("front")
        self.assertEqual(len(processes), 1)
        mock_process_instance.start.assert_called()

    @patch("signal.signal")
    def test_setup_signal_handlers(self, mock_signal: MagicMock) -> None:
        """
        Test the setup_signal_handlers function.

        :param MagicMock mock_signal: Mocked signal.signal function
        """
        processes: List[MagicMock] = [MagicMock()]
        setup_signal_handlers(processes)
        self.assertEqual(mock_signal.call_count, 2)

    def test_wait_for_processes(self) -> None:
        """
        Test the wait_for_processes function.
        """
        mock_process = MagicMock()
        processes: List[MagicMock] = [mock_process]
        wait_for_processes(processes)
        mock_process.join.assert_called_once()

    @patch("uvicorn.run")
    def test_run_api(self, mock_uvicorn_run: MagicMock) -> None:
        """
        Test the run_api function.

        :param MagicMock mock_uvicorn_run: Mocked uvicorn.run function
        """
        with patch.dict(os.environ, self.env_vars, clear=True):
            run_api()
            mock_uvicorn_run.assert_called_once_with(app="api.app:app", port=8000, host="localhost", log_level="debug")

    @patch("subprocess.run")
    def test_run_front(self, mock_subprocess_run: MagicMock) -> None:
        """
        Test the run_front function.

        :param MagicMock mock_subprocess_run: Mocked subprocess.run function
        """
        with patch.dict(os.environ, self.env_vars, clear=True):
            run_front()
            mock_subprocess_run.assert_called_once()
            args, _ = mock_subprocess_run.call_args
            self.assertEqual(args[0][0], "streamlit")
            self.assertEqual(args[0][2], "front/app.py")


if __name__ == "__main__":
    unittest.main()
