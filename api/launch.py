import logging
import multiprocessing
import os
import sys

import click
import uvicorn

# Add the parent directory to sys.path to allow imports from the api package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.models.environement import Environment


@click.command()
@click.option(
    "--env",
    type=click.Choice([env.value for env in Environment]),
    default=Environment.DEV.value,
    help="Specify the environment (dev or prod)",
)
@click.option("--host", default="0.0.0.0", help="The host to bind the server to")
@click.option("--port", default=8000, help="The port to bind the server to")
def run_api(env: str, host: str, port: int) -> None:
    """
    Run the FastAPI application in either development or production mode.

    :param str env: The environment to run the API in (dev or prod)
    :param str host: The host to bind the server to
    :param int port: The port to bind the server to
    """
    common_config = {
        "app": "api.app:app",
        "host": host,
        "port": port,
    }

    if env == Environment.DEV.value:
        click.echo(" 💡 Starting API in development mode")
        config = {
            **common_config,
            "reload": True,
            "workers": 1,
            "log_level": "debug",
        }
    else:
        click.echo(" 💡 Starting API in production mode")
        num_workers = multiprocessing.cpu_count()
        config = {
            **common_config,
            "workers": num_workers,
            "log_level": "info",
        }

    click.echo(f" ✅ Server is running on http://{host}:{port}")
    click.echo(" 💡 Press CTRL+C to quit")

    uvicorn.run(**config)


if __name__ == "__main__":
    run_api()
