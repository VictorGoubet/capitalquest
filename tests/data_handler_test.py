import unittest

from api.data.data_handler import DataHandler
from api.models.country import Country


class TestDataHandler(unittest.TestCase):
    """Test cases for the DataHandler class."""

    def test_get_random_country(self):
        """
        Test getting a random country.

        This test ensures that the get_random_country method returns a valid Country object
        and that its name is one of the countries in the test dataset.
        """
        handler = DataHandler()
        random_country = handler.get_random_country()
        self.assertIsInstance(random_country, Country)

        # Get all country names from the handler
        all_country_names = {country.name for country in handler.get_all_countries()}

        # Assert that the random country's name is in the set of all country names
        self.assertIn(random_country.name, all_country_names)

    def test_search_country(self):
        """Test searching for a country by name or code."""
        handler = DataHandler()

        france = handler.search_country("France")
        self.assertIsInstance(france, Country)
        self.assertEqual(france.name, "France")
        self.assertEqual(france.code, "FR")

        france_by_code = handler.search_country("FR")
        self.assertEqual(france, france_by_code)

        self.assertIsNone(handler.search_country("Invalid"))

    def test_get_all_countries(self):
        """Test getting all countries."""
        handler = DataHandler()

        all_countries = handler.get_all_countries()
        self.assertIsInstance(all_countries, frozenset)
        self.assertEqual(len(all_countries), 192)

        # Check if some expected countries are in the set
        expected_countries = {"France", "Germany", "United States", "Japan", "Brazil"}
        country_names = {country.name for country in all_countries}
        self.assertTrue(expected_countries.issubset(country_names))

        # Check if the number of unique country names matches the total count
        self.assertEqual(len(country_names), 192)

    def test_create_indexes(self):
        """Test creation of name and code indexes."""
        handler = DataHandler()

        self.assertIn("france", handler._name_index)
        self.assertIn("fr", handler._code_index)
        self.assertIn("germany", handler._name_index)
        self.assertIn("de", handler._code_index)

        self.assertEqual(handler._name_index["france"], handler._code_index["fr"])
        self.assertEqual(handler._name_index["germany"], handler._code_index["de"])


if __name__ == "__main__":
    unittest.main()
