import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.data.instance import get_data_handler
from api.routes import all_countries, random_country, search_country

# Configure logging
log_level = os.environ.get("UVICORN_LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


get_data_handler()

app = FastAPI(
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
version = "v1"
prefix = f"/api/{version}"
app.include_router(all_countries.router, prefix=prefix, tags=["Countries"])
app.include_router(random_country.router, prefix=prefix, tags=["Countries"])
app.include_router(search_country.router, prefix=prefix, tags=["Countries"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=log_level.lower())
