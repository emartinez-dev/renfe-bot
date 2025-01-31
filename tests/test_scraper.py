import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from scraper import Scraper, extract_dwr_token, create_cookiedict, create_search_id, create_session_script_id
from models import StationRecord
from errors import InvalidTrainRideFilter, InvalidDWRToken

class TestScraper(unittest.TestCase):
    def setUp(self):
        # Setup mock data for testing
        self.origin = StationRecord(name="Madrid", code="MAD")
        self.destination = StationRecord(name="Barcelona", code="BCN")
        self.departure_date = datetime(2025, 1, 31, 10, 0)
        self.return_date = datetime(2025, 2, 1, 10, 0)
        
        self.scraper = Scraper(
            origin=self.origin, 
            destination=self.destination, 
            departure_date=self.departure_date, 
            return_date=self.return_date
        )
    
    @patch('scraper.requests.Session.post')
    def test_get_trainrides(self, mock_post):
        # Mock the HTTP responses for the scraper methods
        mock_post.return_value.ok = True
        mock_post.return_value.text = '{"listadoTrenes": []}'  # mock response for getting train list

        # Mock necessary functions
        self.scraper._do_search = MagicMock()
        self.scraper._do_get_dwr_token = MagicMock()
        self.scraper._do_update_session_objects = MagicMock()
        self.scraper._do_get_train_list = MagicMock(return_value={"listadoTrenes": []})

        # Test if get_trainrides returns an empty list when no trains are found
        result = self.scraper.get_trainrides()
        self.assertEqual(result, [])
    
    def test_invalid_trainride_filter(self):
        # Test the case where return_date is before departure_date
        with self.assertRaises(InvalidTrainRideFilter):
            Scraper(
                origin=self.origin, 
                destination=self.destination, 
                departure_date=self.departure_date, 
                return_date=datetime(2025, 1, 30, 10, 0)  # Invalid return date
            )
    
    @patch('scraper.extract_dwr_token')
    def test_extract_dwr_token(self, mock_extract_dwr_token):
        # Test extracting the DWR token with a valid response
        mock_response = 'throw #DWR-REPLY\nr.handleCallback("1","0","12345");'
        mock_extract_dwr_token.return_value = '12345'
        token = extract_dwr_token(mock_response)
        self.assertEqual(token, '12345')

    def test_extract_dwr_token_invalid(self):
        # Test extracting the DWR token with an invalid response
        with self.assertRaises(InvalidDWRToken):
            extract_dwr_token('Invalid response')
    
    def test_create_cookiedict(self):
        # Test the creation of cookies for the search
        cookies = create_cookiedict(self.origin, self.destination)
        self.assertIn("Search", cookies["name"])
        self.assertIn(self.origin.code, cookies["value"])
    
    def test_create_search_id(self):
        # Test the creation of search_id
        search_id = create_search_id()
        self.assertTrue(search_id.startswith('_'))
        self.assertEqual(len(search_id), 5)
    
    def test_create_session_script_id(self):
        # Test the creation of session script ID
        with patch('scraper.tokenify', return_value='test_token'):
            script_id = create_session_script_id('dwr_token')
            self.assertTrue(script_id.startswith('dwr_token/'))
            self.assertIn('test_token', script_id)

if __name__ == "__main__":
    unittest.main()
