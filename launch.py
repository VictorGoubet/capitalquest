import logging
import os
import signal
import subprocess
import sys
from multiprocessing import Process
from typing import Callable, List, Optional

import click
import uvicorn

# Constants for default values
DEFAULT_API_HOST: str = "localhost"
DEFAULT_API_PORT: int = 8000
DEFAULT_FRONT_HOST: str = "localhost"
DEFAULT_FRONT_PORT: int = 8051
DEFAULT_ENV: str = "dev"

# Configure logging
logging.basicConfig(level=logging.INFO, format="\033[32m%(levelname)s\033[0m:     %(message)s")
logger: logging.Logger = logging.getLogger(__name__)


def set_log_level(env: str) -> None:
    """
    Set the log level based on the environment.

    :param str env: The current environment (dev or prod)
    """
    log_level: int = logging.DEBUG if env == "dev" else logging.INFO
    logging.getLogger().setLevel(log_level)
    logger.setLevel(log_level)


def run_api() -> None:
    """
    Run the API component.
    """
    api_port: str = os.environ["api_port"]
    api_host: str = os.environ["api_host"]
    env: str = os.environ["environment"]
    log_level: str = "debug" if env == "dev" else "info"

    logger.info(f" ✅ Starting API on http://{api_host}:{api_port}")
    uvicorn.run(app="api.app:app", port=int(api_port), host=api_host, log_level=log_level)


def run_front() -> None:
    """
    Run the front-end component.
    """
    front_port: str = os.environ["front_port"]
    front_host: str = os.environ["front_host"]
    logger.info(f" ✅ Starting front-end on http://{front_host}:{front_port}")
    streamlit_command: List[str] = [
        "streamlit",
        "run",
        "front/app.py",
        "--server.port",
        str(front_port),
        "--server.address",
        front_host,
        "--logger.level",
        "info",
    ]
    subprocess.run(streamlit_command)


def set_environment_variable(key: str, value: Optional[str], default: str) -> None:
    """
    Set an environment variable with a fallback to a default value.
    """
    os.environ[key] = str(value if value is not None else os.getenv(key, default))


def set_environment_variables(
    api_host: Optional[str],
    api_port: Optional[int],
    front_host: Optional[str],
    front_port: Optional[int],
    env: Optional[str],
) -> None:
    """
    Set environment variables for the application.

    This function sets the environment variables for the API host and port,
    front-end host and port, and the environment type. If any of the parameters
    are None, it falls back to environment variables or default values.

    :param Optional[str] api_host: The host for the API server, defaults to '0.0.0.0' if not set
    :param Optional[int] api_port: The port for the API server, defaults to '8000' if not set
    :param Optional[str] front_host: The host for the front-end server, defaults to '0.0.0.0' if not set
    :param Optional[int] front_port: The port for the front-end server, defaults to '8051' if not set
    :param Optional[str] env: The environment type (dev or prod), defaults to 'dev' if not set
    """
    set_environment_variable("api_host", api_host, DEFAULT_API_HOST)
    set_environment_variable("api_port", api_port, DEFAULT_API_PORT)
    set_environment_variable("front_host", front_host, DEFAULT_FRONT_HOST)
    set_environment_variable("front_port", front_port, DEFAULT_FRONT_PORT)
    set_environment_variable("environment", env, DEFAULT_ENV)
    set_log_level(os.environ["environment"])


@click.command()
@click.option("--env", type=click.Choice(["dev", "prod", None]), default=None, help="Specify the environment")
@click.option("--api-host", type=Optional[str], default=None, help="The host to bind the API server to")
@click.option("--api-port", type=Optional[int], default=None, help="The port to bind the API server to")
@click.option("--front-host", default=None, help="The host to bind the front-end server to")
@click.option("--front-port", default=None, help="The port to bind the front-end server to")
@click.option("--component", type=click.Choice(["api", "front", "both"]), default="both", help="The component to run")
def run_app(
    env: Optional[str],
    api_host: Optional[str],
    api_port: Optional[int],
    front_host: Optional[str],
    front_port: Optional[int],
    component: str,
) -> None:
    """
    Run the application components (API, front-end, or both) in either development or production mode.

    :param Optional[str] env: The environment to run the application in (dev or prod)
    :param Optional[str] api_host: The host to bind the API server to
    :param Optional[int] api_port: The port to bind the API server to
    :param Optional[str] front_host: The host to bind the front-end server to
    :param Optional[int] front_port: The port to bind the front-end server to
    :param str component: The component to run (api, front, or both)
    """
    set_environment_variables(api_host, api_port, front_host, front_port, env)
    processes: List[Process] = start_components(component)
    setup_signal_handlers(processes)
    wait_for_processes(processes)


def start_components(component: str) -> List[Process]:
    """
    Start the specified components of the application.

    :param str component: The component to run (api, front, or both)
    :return List[Process]: A list of started processes
    """
    processes: List[Process] = []

    def run_component(target_func: Callable[[], None]) -> None:
        process: Process = Process(target=target_func)
        processes.append(process)
        process.start()

    if component == "api":
        run_component(run_api)
    elif component == "front":
        run_component(run_front)
    else:  # component == "both"
        run_component(run_api)
        run_component(run_front)

    logger.info(" 💡 Press CTRL+C to quit")
    return processes


def setup_signal_handlers(processes: List[Process]) -> None:
    """
    Set up signal handlers for graceful shutdown.

    :param List[Process] processes: A list of running processes
    """

    def signal_handler(signum: int, frame: Optional[object]) -> None:
        stop_processes(processes)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def stop_processes(processes: List[Process]) -> None:
    """
    Stop all running processes.

    :param List[Process] processes: A list of running processes
    """
    logger.warning("\n ⚠️ Stopping all processes...")
    for process in processes:
        if process.is_alive():
            process.terminate()

    for process in processes:
        process.join(timeout=5)
        if process.is_alive():
            logger.error(f" ❌ Process {process.pid} did not terminate gracefully. Killing it.")
            process.kill()
            process.join()

    logger.info(" ✅ All processes stopped")
    sys.exit(0)


def wait_for_processes(processes: List[Process]) -> None:
    """
    Wait for all processes to complete.

    :param List[Process] processes: A list of running processes
    """
    for process in processes:
        process.join()


if __name__ == "__main__":
    run_app()
