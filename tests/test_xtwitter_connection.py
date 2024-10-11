import unittest
from unittest.mock import Mock, patch
from masa_ai.connections.xtwitter_connection import XTwitterConnection
from masa_ai.tools.qc.exceptions import RateLimitException, NoWorkersAvailableException, APIException, AuthenticationException
from masa_ai.tools.qc.qc_manager import QCManager

class TestXTwitterConnection(unittest.TestCase):
    def setUp(self):
        self.connection = XTwitterConnection()

    @patch('masa_ai.connections.xtwitter_connection.XTwitterConnection._make_request')
    def test_get_tweets_success(self, mock_make_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "1", "text": "Test tweet"}]}
        mock_make_request.return_value = mock_response

        result = self.connection.get_tweets('endpoint', 'query', 10)

        self.assertEqual(result, {"data": [{"id": "1", "text": "Test tweet"}]})
        mock_make_request.assert_called_once_with('POST', 'https://api.twitter.com/2/endpoint', data={'query': 'query', 'count': 10})

    @patch('masa_ai.connections.xtwitter_connection.XTwitterConnection._make_request')
    def test_rate_limit_exception(self, mock_make_request):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_make_request.return_value = mock_response

        with self.assertRaises(RateLimitException):
            self.connection.get_tweets('endpoint', 'query', 10)

    @patch('masa_ai.connections.xtwitter_connection.XTwitterConnection._make_request')
    def test_no_workers_available_exception(self, mock_make_request):
        mock_response = Mock()
        mock_response.status_code = 417
        mock_make_request.return_value = mock_response

        with self.assertRaises(NoWorkersAvailableException):
            self.connection.get_tweets('endpoint', 'query', 10)

    @patch('masa_ai.connections.xtwitter_connection.XTwitterConnection._make_request')
    def test_gateway_timeout_exception(self, mock_make_request):
        mock_response = Mock()
        mock_response.status_code = 504
        mock_make_request.return_value = mock_response

        with self.assertRaises(APIException):
            self.connection.get_tweets('endpoint', 'query', 10)

    @patch('masa_ai.connections.xtwitter_connection.XTwitterConnection._make_request')
    def test_authentication_exception(self, mock_make_request):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_make_request.return_value = mock_response

        with self.assertRaises(AuthenticationException):
            self.connection.get_tweets('endpoint', 'query', 10)

    @patch('masa_ai.connections.xtwitter_connection.XTwitterConnection._make_request')
    @patch('masa_ai.tools.qc.retry_manager.RetryPolicy.wait_time')
    def test_retry_logic(self, mock_wait_time, mock_make_request):
        mock_response_fail = Mock()
        mock_response_fail.status_code = 429
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": [{"id": "1", "text": "Test tweet"}]}
        
        mock_make_request.side_effect = [mock_response_fail, mock_response_success]
        mock_wait_time.return_value = 0  # Don't actually wait in tests

        result = self.connection.get_tweets('endpoint', 'query', 10)

        self.assertEqual(result, {"data": [{"id": "1", "text": "Test tweet"}]})
        self.assertEqual(mock_make_request.call_count, 2)

if __name__ == '__main__':
    unittest.main()
