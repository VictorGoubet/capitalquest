import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.app import app
from api.data.data_handler import DataHandler
from api.models.country import Country


class TestCountryAPI(unittest.TestCase):
    """Test cases for the Country Information API."""

    def setUp(self) -> None:
        """
        Set up the test client and mock data.
        """
        self.client = TestClient(app)
        self.mock_country = Country(
            name="Test Country",
            code="TC",
            population=1000000,
            capital="Test Capital",
            area=100000,
            currency="Test Currency",
            language="Test Language",
        )

    @patch.object(DataHandler, "get_all_countries")
    def test_all_countries_endpoint(self, mock_get_all_countries: MagicMock) -> None:
        """
        Test the all countries endpoint.

        :param MagicMock mock_get_all_countries: Mocked get_all_countries method
        """
        mock_get_all_countries.return_value = [self.mock_country]
        response = self.client.get("/api/v1/all-countries")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["name"], "Test Country")

    @patch.object(DataHandler, "get_random_country")
    def test_random_country_endpoint(self, mock_get_random_country: MagicMock) -> None:
        """
        Test the random country endpoint.

        :param MagicMock mock_get_random_country: Mocked get_random_country method
        """
        mock_get_random_country.return_value = self.mock_country
        response = self.client.get("/api/v1/random-country")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["name"], "Test Country")

    @patch.object(DataHandler, "search_country")
    def test_search_country_endpoint(self, mock_search_country: MagicMock) -> None:
        """
        Test the search country endpoint.

        :param MagicMock mock_search_country: Mocked search_country method
        """
        mock_search_country.return_value = self.mock_country
        response = self.client.get("/api/v1/search-country/TC")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["name"], "Test Country")


if __name__ == "__main__":
    unittest.main()
