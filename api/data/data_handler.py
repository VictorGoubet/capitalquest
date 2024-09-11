import csv
import logging
import random
from pathlib import Path
from typing import Dict, FrozenSet, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from api.models.country import Country

logger = logging.getLogger(__name__)


class DataHandler(BaseModel):
    """
    A pydantic class to handle loading, indexing, and retrieving country data from a CSV file.
    """

    csv_file_name: str = Field("countries.csv", description="Name of the CSV file containing country data")

    _csv_file_path: Path = PrivateAttr()
    _countries: FrozenSet[Country] = PrivateAttr(default_factory=frozenset)
    _name_index: Dict[str, Country] = PrivateAttr(default_factory=dict)
    _code_index: Dict[str, Country] = PrivateAttr(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: dict) -> None:
        """
        Initialize the DataHandler, load countries, and create indexes.

        :param **data: Additional keyword arguments for pydantic model initialization.
        """
        super().__init__(**data)
        self._csv_file_path = Path(__file__).parent / self.csv_file_name
        self._load_countries()
        self._create_indexes()

    def _load_countries(self) -> None:
        """
        Load countries from the CSV file and convert them to Country objects.
        Skips countries with missing name or capital.
        """
        countries: list[Country] = []
        try:
            with open(self._csv_file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if not row.get("Country") or not row.get("Capital/Major City"):
                        continue
                    try:
                        country: Country = Country.model_validate(row)
                        countries.append(country)
                    except ValueError as e:
                        logger.error(f" ❌ Error parsing country: {e}")
        except IOError as e:
            logger.error(f" ❌ Error reading CSV file: {e}")
        self._countries = frozenset(countries)
        logger.info(f" ✅ {len(self._countries)} countries loaded from {self._csv_file_path}")

    def _create_indexes(self) -> None:
        """
        Create indexes for fast retrieval by name and code.
        """
        for country in self._countries:
            self._name_index[country.name.lower()] = country
            if country.code:
                self._code_index[country.code.lower()] = country

    def get_random_country(self) -> Optional[Country]:
        """
        Get a random country from the loaded data.

        :return Optional[Country]: A randomly selected Country object, or None if no countries are loaded.
        """
        if not self._countries:
            return None
        return random.choice(list(self._countries))

    def get_all_countries(self) -> FrozenSet[Country]:
        """
        Get all loaded countries.

        :return FrozenSet[Country]: A frozen set of all loaded Country objects.
        """
        return self._countries

    def search_country(self, query: str) -> Optional[Country]:
        """
        Search for a country by name or code.

        :param str query: The search query (country name or code).
        :return Optional[Country]: The matching Country object, or None if not found.
        """
        query = query.lower()
        return self._name_index.get(query) or self._code_index.get(query)
