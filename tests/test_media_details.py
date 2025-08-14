import unittest
from unittest.mock import patch, Mock
import os
import sys
import requests

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.media_details import get_jellyfin_media_details

class TestJellyfinMediaDetails(unittest.TestCase):

    @patch('utils.media_details.requests.get')
    @patch('utils.media_details.JELLYFIN_USER_ID', 'fake-user-id')
    @patch('utils.media_details.JELLYFIN_API_KEY', 'fake-key')
    @patch('utils.media_details.JELLYFIN_API_URL', 'http://fake-jellyfin:8096')
    def test_get_jellyfin_media_details_success(self, mock_requests_get):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "MediaStreams": [
                {"Type": "Video", "Codec": "hevc", "Height": 2160, "VideoRange": "HDR"},
                {"Type": "Audio", "DisplayTitle": "English 5.1 (DTS-HD MA)", "Language": "eng"},
                {"Type": "Audio", "DisplayTitle": "French 5.1 (AC3)", "Language": "fre"},
                {"Type": "Subtitle", "DisplayTitle": "English (SRT)", "Language": "eng"},
                {"Type": "Subtitle", "DisplayTitle": "French (SRT)", "Language": "fre"}
            ]
        }
        mock_requests_get.return_value = mock_response

        expected_details = {
            'video': {'resolution': '2160p', 'codec': 'HEVC', 'hdr': 'HDR'},
            'audio': ['English 5.1 (DTS-HD MA) (ENG)', 'French 5.1 (AC3) (FRE)'],
            'subtitles': ['ENG', 'FRE']
        }

        # Act
        result = get_jellyfin_media_details("some_item_id")

        # Assert
        self.assertEqual(result, expected_details)
        mock_requests_get.assert_called_once_with(
            "http://fake-jellyfin:8096/Users/fake-user-id/Items/some_item_id",
            headers={'X-Emby-Token': 'fake-key'},
            timeout=10
        )

    @patch('utils.media_details.requests.get')
    @patch('utils.media_details.JELLYFIN_USER_ID', 'fake-user-id')
    @patch('utils.media_details.JELLYFIN_API_KEY', 'fake-key')
    @patch('utils.media_details.JELLYFIN_API_URL', 'http://fake-jellyfin:8096')
    def test_get_jellyfin_media_details_api_error(self, mock_requests_get):
        # Arrange
        mock_requests_get.side_effect = requests.exceptions.RequestException("API is down")

        # Act
        result = get_jellyfin_media_details("some_item_id")

        # Assert
        self.assertEqual(result, {})

    @patch('utils.media_details.JELLYFIN_USER_ID', None)
    @patch('utils.media_details.JELLYFIN_API_KEY', 'fake-key')
    @patch('utils.media_details.JELLYFIN_API_URL', 'http://fake-jellyfin:8096')
    def test_get_jellyfin_media_details_no_config(self):
        # Act
        result = get_jellyfin_media_details("some_item_id")

        # Assert
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
