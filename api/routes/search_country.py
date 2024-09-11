from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from api.data.data_handler import DataHandler
from api.data.instance import get_data_handler
from api.models.country import Country

router: APIRouter = APIRouter()


@router.get(
    "/search-country/{query}",
    response_model=Country,
    status_code=status.HTTP_200_OK,
    summary="Search for a country",
    description="Search for a country by name or code in the database.",
    response_description="Successfully found a country matching the query",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "message": " ✅ Successfully found a country matching the query",
                        "data": Country.model_config["json_schema_extra"]["examples"][0],
                    }
                }
            },
        },
        404: {
            "description": "No country found matching the query",
            "content": {"application/json": {"example": {"detail": " ❌ No country found matching 'XYZ'."}}},
        },
    },
    tags=["Countries"],
)
async def search_country(
    data_handler: DataHandler = Depends(get_data_handler),
    query_input: str = Query(None, description="The search query (country name or code)", example="United States"),
) -> JSONResponse:
    """
    Search for a country by name or code.

    :param DataHandler data_handler: The data handler instance (injected by FastAPI)
    :param str query: The search query (country name or code). Defaults to "France".
    :return JSONResponse: A JSON response containing a success message and information about the matched country.
    :raises HTTPException: If no country is found matching the query.
    """
    country: Country | None = data_handler.search_country(query_input)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f" ❌ No country found matching '{query_input}'."
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f" ✅ Successfully found a country matching '{query_input}'",
            "data": country.model_dump(),
        },
    )
