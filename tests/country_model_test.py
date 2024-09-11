import unittest
from typing import Dict

from pydantic import ValidationError

from api.models.country import Country


class TestCountry(unittest.TestCase):
    """Test cases for the Country model."""

    def test_country_creation(self) -> None:
        """Test the creation of a Country instance."""
        country_data: Dict[str, str] = {
            "Country": "France",
            "Abbreviation": "FR",
            "Population": "67,391,582",
            "Capital/Major City": "Paris",
            "Land Area(Km2)": "551,695",
            "Currency-Code": "Euro",
            "Official language": "French",
        }
        country: Country = Country(**country_data)
        self.assertEqual(country.name, "France")
        self.assertEqual(country.code, "FR")
        self.assertEqual(country.population, 67391582)
        self.assertEqual(country.capital, "Paris")
        self.assertEqual(country.area, 551695)
        self.assertEqual(country.currency, "Euro")
        self.assertEqual(country.language, "French")

    def test_country_validation(self) -> None:
        """Test the validation of Country model fields."""
        # Test valid country creation
        valid_country: Country = Country(
            Country="Valid",
            Abbreviation="VA",
            Population="1000000",
            **{"Capital/Major City": "Test", "Land Area(Km2)": "100000", "Currency-Code": "Test"},
            **{"Official language": "Test language"}
        )
        self.assertEqual(valid_country.name, "Valid")
        self.assertEqual(valid_country.code, "VA")
        self.assertEqual(valid_country.population, 1000000)
        self.assertEqual(valid_country.area, 100000)
        self.assertEqual(valid_country.language, "Test")

        # Test invalid country creation
        invalid_data: Dict[str, str] = {
            "Country": "Invalid",
            "Abbreviation": "I",  # Should be at least 2 characters
            "Population": "0",  # Should be greater than 0
            "Capital/Major City": "Test",
            "Land Area(Km2)": "0",  # Should be greater than 0
            "Currency-Code": "",
            "Official language": "",
        }
        country: Country = Country(**invalid_data)

        # Check that invalid values are set to None
        self.assertIsNone(country.code)
        self.assertIsNone(country.population)
        self.assertIsNone(country.area)
        self.assertIsNone(country.currency)
        self.assertIsNone(country.language)

        # Test that other fields are still valid
        self.assertEqual(country.name, "Invalid")
        self.assertEqual(country.capital, "Test")

        # Test language cleaning
        country_with_language: Country = Country(
            Country="Test", **{"Capital/Major City": "Test"}, **{"Official language": "Test language"}
        )
        self.assertEqual(country_with_language.language, "Test")

    def test_optional_fields(self) -> None:
        """Test the optional fields of the Country model."""
        country_data: Dict[str, str] = {
            "Country": "Test Country",
            "Abbreviation": "TC",
            "Population": "1,000,000",
            "Capital/Major City": "Test Capital",
            "Land Area(Km2)": "100,000",
        }
        country: Country = Country(**country_data)
        self.assertIsNone(country.currency)
        self.assertIsNone(country.language)

    def test_country_hash(self) -> None:
        """Test the hash function of the Country model."""
        country1: Country = Country(
            Country="Test",
            Abbreviation="TS",
            Population="1,000,000",
            **{"Capital/Major City": "Test", "Land Area(Km2)": "100,000", "Currency-Code": "Test"},
            **{"Official language": "Test"}
        )
        country2: Country = Country(
            Country="Test",
            Abbreviation="TS",
            Population="1,000,000",
            **{"Capital/Major City": "Test", "Land Area(Km2)": "100,000", "Currency-Code": "Test"},
            **{"Official language": "Test"}
        )
        self.assertEqual(hash(country1), hash(country2))

    def test_country_immutability(self) -> None:
        """Test the immutability of the Country model."""
        country: Country = Country(
            Country="Test",
            Abbreviation="TS",
            Population="1,000,000",
            **{"Capital/Major City": "Test", "Land Area(Km2)": "100,000"}
        )

        with self.assertRaises(ValidationError) as context:
            country.name = "New Name"

        self.assertIn("Instance is frozen", str(context.exception))

    def test_parse_number(self) -> None:
        """Test the parse_number validator."""
        country: Country = Country(
            Country="Test",
            Abbreviation="TS",
            Population="1,000,000",
            **{"Capital/Major City": "Test", "Land Area(Km2)": "100,000"}
        )
        self.assertEqual(country.population, 1000000)
        self.assertEqual(country.area, 100000)

    def test_clean_language(self) -> None:
        """Test the clean_language validator."""
        country: Country = Country(
            Country="Test",
            Abbreviation="TS",
            Population="1,000,000",
            **{"Capital/Major City": "Test", "Land Area(Km2)": "100,000", "Official language": "English language"}
        )
        self.assertEqual(country.language, "English")

    def test_validate_code(self) -> None:
        """Test the validate_code validator."""
        country_with_short_code: Country = Country(Country="Test", Abbreviation="T", **{"Capital/Major City": "Test"})
        self.assertIsNone(country_with_short_code.code)

        country_with_valid_code: Country = Country(Country="Test", Abbreviation="TS", **{"Capital/Major City": "Test"})
        self.assertEqual(country_with_valid_code.code, "TS")

    def test_validate_fields(self) -> None:
        """Test the validate_fields model validator."""
        country: Country = Country(
            Country="Test",
            **{"Capital/Major City": "Test"},
            Population="0",
            **{"Land Area(Km2)": "0"},
            **{"Currency-Code": "", "Official language": ""}
        )
        self.assertIsNone(country.population)
        self.assertIsNone(country.area)
        self.assertIsNone(country.currency)
        self.assertIsNone(country.language)
