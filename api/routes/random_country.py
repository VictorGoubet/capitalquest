from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.data.data_handler import DataHandler
from api.data.instance import get_data_handler
from api.models.country import Country

router = APIRouter()


@router.get(
    "/random-country",
    response_model=Country,
    status_code=status.HTTP_200_OK,
    summary="Get a random country",
    description="Retrieve information about a randomly selected country from the database.",
    response_description="Successfully retrieved a random country",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "message": " ✅ Successfully retrieved a random country",
                        "data": Country.model_config["json_schema_extra"]["examples"],
                    }
                }
            },
        },
        404: {
            "description": "No countries found in the database",
            "content": {"application/json": {"example": {"detail": " ❌ No countries found in the database."}}},
        },
    },
    tags=["Countries"],
)
async def get_random_country(data_handler: DataHandler = Depends(get_data_handler)) -> Dict[str, Any]:
    """
    Retrieve a random country from the database.

    :param DataHandler data_handler: The data handler instance (injected by FastAPI)
    :return Dict[str, Any]: A dictionary containing a success message and information about a random  country.
    :raises HTTPException: If no country is found in the database.
    """
    random_country = data_handler.get_random_country()
    if random_country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" ❌ No countries found in the database.")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": " ✅ Successfully retrieved a random country", "data": random_country.model_dump()},
    )
