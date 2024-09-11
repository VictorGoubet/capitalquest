from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.data.data_handler import DataHandler
from api.data.instance import get_data_handler
from api.models.country import Country

router = APIRouter()


@router.get(
    "/all-countries",
    response_model=List[Country],
    status_code=status.HTTP_200_OK,
    summary="Get all countries",
    description="Retrieve information about all countries from the database.",
    response_description="Successfully retrieved all countries",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "message": " ✅ Successfully retrieved all countries",
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
async def get_all_countries(data_handler: DataHandler = Depends(get_data_handler)) -> Dict[str, Any]:
    """
    Retrieve all countries from the database.

    :param DataHandler data_handler: The data handler instance (injected by FastAPI)
    :return Dict[str, Any]: A dictionary containing a success message and a list of all countries.
    :raises HTTPException: If no countries are found in the database.
    """
    all_countries = data_handler.get_all_countries()
    if not all_countries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" ❌ No countries found in the database.")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": " ✅ Successfully retrieved all countries",
            "data": [country.model_dump() for country in all_countries],
        },
    )
