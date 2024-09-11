import unittest
from unittest.mock import patch

from api.data.data_handler import DataHandler
from api.models.country import Country


class TestDataHandler(unittest.TestCase):
    """Test cases for the DataHandler class."""

    def test_get_random_country(self):
        """Test getting a random country."""
        with patch.object(DataHandler, "_load_countries"):
            handler = DataHandler()
            handler._countries = frozenset(
                [
                    Country(
                        name="France",
                        code="FR",
                        population=67391582,
                        capital="Paris",
                        area=551695.0,
                        currency="Euro",
                        languages=["French"],
                    ),
                    Country(
                        name="Germany",
                        code="DE",
                        population=83190556,
                        capital="Berlin",
                        area=357386.0,
                        currency="Euro",
                        languages=["German"],
                    ),
                ]
            )
            random_country = handler.get_random_country()
            self.assertIsInstance(random_country, Country)
            self.assertIn(random_country.name, ["France", "Germany"])

    def test_search_country(self):
        """Test searching for a country by name or code."""
        with patch.object(DataHandler, "_load_countries"):
            handler = DataHandler()
            france = Country(
                name="France",
                code="FR",
                population=67391582,
                capital="Paris",
                area=551695.0,
                currency="Euro",
                languages=["French"],
            )
            handler._name_index = {"france": france}
            handler._code_index = {"fr": france}

            self.assertEqual(handler.search_country("France"), france)
            self.assertEqual(handler.search_country("FR"), france)
            self.assertIsNone(handler.search_country("Invalid"))

    def test_get_all_countries(self):
        """Test getting all countries."""
        with patch.object(DataHandler, "_load_countries"):
            handler = DataHandler()
            france = Country(
                name="France",
                code="FR",
                population=67391582,
                capital="Paris",
                area=551695.0,
                currency="Euro",
                languages=["French"],
            )
            germany = Country(
                name="Germany",
                code="DE",
                population=83190556,
                capital="Berlin",
                area=357386.0,
                currency="Euro",
                languages=["German"],
            )
            handler._countries = frozenset([france, germany])

            all_countries = handler.get_all_countries()
            self.assertIsInstance(all_countries, frozenset)
            self.assertEqual(len(all_countries), 2)
            self.assertIn(france, all_countries)
            self.assertIn(germany, all_countries)


if __name__ == "__main__":
    unittest.main()
