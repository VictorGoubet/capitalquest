import multiprocessing
import signal
import subprocess
import sys
from enum import Enum
from typing import Any, Dict, List

import click
import uvicorn
from pydantic import BaseModel, ConfigDict


class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"


class Config(BaseModel):
    """Configuration for the application components."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    app: str
    api_host: str
    api_port: int
    front_host: str
    front_port: int
    reload: bool = False
    workers: int = 1
    log_level: str = "info"


def run_api(config: Config) -> None:
    """
    Run the API component.

    :param Config config: The configuration for the API
    """
    click.echo(f" ✅ Starting API on http://{config.api_host}:{config.api_port}")
    api_config = {k: v for k, v in config.model_dump().items() if not k.startswith("front_") and v is not None}
    api_config["host"] = api_config.pop("api_host")
    api_config["port"] = api_config.pop("api_port")
    uvicorn.run(**api_config)


def run_front(config: Config) -> None:
    """
    Run the front-end component.

    :param Config config: The configuration for the front-end
    """
    click.echo(f" ✅ Starting front-end on http://{config.front_host}:{config.front_port}")
    streamlit_command = [
        "streamlit",
        "run",
        "front/app.py",
        "--server.port",
        str(config.front_port),
        "--server.address",
        config.front_host,
        "--",
        "--api_host",
        config.api_host,
        "--api_port",
        str(config.api_port),
    ]
    subprocess.run(streamlit_command)


@click.command()
@click.option(
    "--env",
    type=click.Choice([env.value for env in Environment]),
    default=Environment.DEV.value,
    help="Specify the environment (dev or prod)",
)
@click.option("--api-host", default="0.0.0.0", help="The host to bind the API server to")
@click.option("--api-port", default=8000, help="The port to bind the API server to")
@click.option("--front-host", default="0.0.0.0", help="The host to bind the front-end server to")
@click.option("--front-port", default=8501, help="The port to bind the front-end server to")
@click.option(
    "--component",
    type=click.Choice(["api", "front", "both"]),
    default="both",
    help="Specify which component to run (api, front, or both)",
)
def run_app(
    env: str,
    api_host: str,
    api_port: int,
    front_host: str,
    front_port: int,
    component: str,
) -> None:
    """
    Run the application components (API, front-end, or both) in either development or production mode.

    :param str env: The environment to run the application in (dev or prod)
    :param str api_host: The host to bind the API server to
    :param int api_port: The port to bind the API server to
    :param str front_host: The host to bind the front-end server to
    :param int front_port: The port to bind the front-end server to
    :param str component: The component to run (api, front, or both)
    """
    common_config: Dict[str, Any] = {
        "app": "api.app:app",
        "api_host": api_host,
        "api_port": api_port,
        "front_host": front_host,
        "front_port": front_port,
    }

    if env == Environment.DEV.value:
        click.echo(" 💡 Starting application in development mode")
        config = Config(reload=True, workers=1, log_level="debug", **common_config)
    else:
        click.echo(" 💡 Starting application in production mode")
        num_workers = multiprocessing.cpu_count()
        config = Config(workers=num_workers, log_level="info", **common_config)

    processes: List[multiprocessing.Process] = []

    def run_component(target_func: callable, config: Config) -> None:
        process = multiprocessing.Process(target=target_func, args=(config,))
        processes.append(process)
        process.start()

    if component == "api":
        run_component(run_api, config)
    elif component == "front":
        run_component(run_front, config)
    else:  # component == "both"
        run_component(run_api, config)
        run_component(run_front, config)

    click.echo(" 💡 Press CTRL+C to quit")

    def signal_handler(signum, frame):
        click.echo("\n ⚠️ Stopping all processes...")
        for process in processes:
            if process.is_alive():
                process.terminate()

        for process in processes:
            process.join(timeout=5)
            if process.is_alive():
                click.echo(f" ❌ Process {process.pid} did not terminate gracefully. Killing it.")
                process.kill()
                process.join()

        click.echo(" ✅ All processes stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    for process in processes:
        process.join()


if __name__ == "__main__":
    run_app()
