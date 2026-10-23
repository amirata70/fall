import unittest
from unittest.mock import patch, MagicMock
import main


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        self.app.testing = True

    def test_webhook_non_json(self):
        response = self.app.post(f'/{main.TOKEN}', data="test")
        self.assertEqual(response.status_code, 403)

    @patch('main.bot.process_new_updates')
    def test_webhook_valid_json(self, mock_process):
        payload = {
            "update_id": 10000,
            "message": {
                "message_id": 1,
                "date": 1441645532,
                "chat": {
                    "id": 111111,
                    "type": "private"
                },
                "text": "/start"
            }
        }
        response = self.app.post(
            f'/{main.TOKEN}',
            json=payload,
            headers={'content-type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'OK')
        mock_process.assert_called_once()

    @patch('main.requests.post')
    def test_analyze_coffee_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "پیش‌بینی فال: آینده‌ای روشن در انتظار شماست."
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = main.analyze_coffee("https://example.com/photo.jpg")
        self.assertIn("آینده‌ای روشن", result)

    @patch('main.requests.post')
    def test_analyze_coffee_failure(self, mock_post):
        mock_post.side_effect = Exception("API Connection Error")
        result = main.analyze_coffee("https://example.com/photo.jpg")
        self.assertIn("خطا در تحلیل تصویر", result)


if __name__ == '__main__':
    unittest.main()
