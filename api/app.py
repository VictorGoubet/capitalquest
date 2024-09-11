from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.data.instance import get_data_handler
from api.routes import all_countries, random_country, search_country

get_data_handler()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    :return FastAPI: The configured FastAPI application
    """
    app: FastAPI = FastAPI(
        title="Country Information API",
        description="An API for retrieving information about countries",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    # Include routes
    prefix: str = "/api"
    app.include_router(all_countries.router, prefix=prefix, tags=["Countries"])
    app.include_router(random_country.router, prefix=prefix, tags=["Countries"])
    app.include_router(search_country.router, prefix=prefix, tags=["Countries"])

    return app


app: FastAPI = create_app()
