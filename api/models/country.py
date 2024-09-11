from typing import Optional

from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_pascal


class Country(BaseModel):
    """
    Pydantic model representing a country.
    """

    name: str = Field(
        ...,
        description="The name of the country",
        alias="Country",
    )
    capital: str = Field(
        ...,
        description="The capital city of the country",
        alias="Capital/Major City",
    )
    population: Optional[int] = Field(
        None,
        description="The population of the country",
        alias="Population",
    )
    code: Optional[str] = Field(
        None,
        description="The ISO 3166-1 alpha-2 country code",
        alias="Abbreviation",
    )
    area: Optional[int] = Field(
        None,
        description="The total area of the country in square kilometers",
        alias="Land Area(Km2)",
    )
    currency: Optional[str] = Field(
        None,
        description="The official currency of the country",
        alias="Currency-Code",
    )
    language: Optional[str] = Field(
        None,
        description="Official language spoken in the country",
        alias="Official language",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        alias_generator=AliasGenerator(serialization_alias=to_pascal),
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "France",
                    "code": "FR",
                    "population": 67391582,
                    "capital": "Paris",
                    "area": 551695,
                    "currency": "Euro",
                    "language": "French",
                },
                {
                    "name": "Japan",
                    "code": "JP",
                    "population": 125360000,
                    "capital": "Tokyo",
                    "area": 377975,
                    "currency": "Japanese yen",
                    "language": "Japanese",
                },
                {
                    "name": "Brazil",
                    "code": "BR",
                    "population": 212559417,
                    "capital": "Brasília",
                    "area": 8515767,
                    "currency": "Brazilian real",
                    "language": "Portuguese",
                },
            ]
        },
        title="Country Information",
        json_encoders={int: lambda v: f"{v:,}"},
    )

    @field_validator("population", "area", mode="before")
    @classmethod
    def parse_number(cls, v: str) -> int:
        """
        Parse string numbers with commas to integers.

        :param str v: The string representation of the number
        :return int: The parsed integer value
        """
        if isinstance(v, str):
            return int(v.replace(",", ""))
        return v

    @field_validator("language", mode="before")
    @classmethod
    def clean_language(cls, v: Optional[str]) -> Optional[str]:
        """
        Remove the word 'language' from the language field if present.

        :param Optional[str] v: The input language string
        :return Optional[str]: The cleaned language string
        """
        if v and isinstance(v, str):
            return v.replace("language", "").strip()
        return v

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """
        Set the code field as None if the code is under 2 characters in length.

        :param Optional[str] v: The input country code
        :return Optional[str]: The validated country code or None
        """
        if v and isinstance(v, str) and len(v) < 2:
            return None
        return v

    @model_validator(mode="after")
    def validate_fields(self) -> "Country":
        """
        Set optional fields to None if they are empty strings or 0 for integers.

        :return Country: The validated Country instance
        """
        for field, field_info in self.model_fields.items():
            if field_info.is_required():
                continue
            value = getattr(self, field)
            if isinstance(value, str) and value.strip() == "":
                object.__setattr__(self, field, None)
            elif isinstance(value, int) and value == 0:
                object.__setattr__(self, field, None)
        return self

    def __hash__(self) -> int:
        """
        Generate a hash for the Country instance.

        :return int: Hash value of the Country instance
        """
        return hash(
            (
                self.name,
                self.code,
                self.population,
                self.capital,
                self.area,
                self.currency,
                self.language,
            )
        )
