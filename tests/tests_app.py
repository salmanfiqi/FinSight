import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory of the 'cik' folder to the Python path
# allows us to import the 'app' module from '../cik/app.py'
# Useful when running the test from a different location (e.g., ./tests/)
sys.path.append(os.path.join(os.path.dirname(__file__), '../cik'))

from app import SecEdgar  # Import the class to test

class TestSecEdgar(unittest.TestCase):
    @patch('app.requests.get')  # Mock 'requests.get' inside the 'app' module
    def test_sec_edgar_initialization(self, mock_get):
        # Sample mocked JSON response simulating SEC company_tickers.json
        mock_json = {
            "0": {"cik_str": 123456, "ticker": "XYZ", "title": "XYZ Corp"}
        }

        # Create a mocked response object
        mock_response = Mock()
        mock_response.json.return_value = mock_json  # Mock .json() to return mock_json
        mock_response.text = str(mock_json)          # Optional: if .text is accessed
        mock_get.return_value = mock_response        # Set this as the return for requests.get

        # Initialize the SecEdgar class with the mock URL
        sec = SecEdgar("https://www.sec.gov/files/company_tickers.json")

        # Assertions
        self.assertEqual(sec.filejson(), mock_json)   # Ensure the filejson method returns the mock
        self.assertIsInstance(sec.namedict, dict)     # namedict should be a dictionary
        self.assertIsInstance(sec.tickerdict, dict)   # tickerdict should also be a dictionary

# Standard entry point to run the test if the file is executed directly
if __name__ == '__main__':
    unittest.main()