import unittest
from unittest.mock import patch, MagicMock
from src.llm import query_llm

class TestLLM(unittest.TestCase):
    @patch('src.llm.client.chat.completions.create')
    def test_query_llm_success(self, mock_create):
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"queries": ["test1", "test2"]}'
        mock_create.return_value = mock_response
        
        result = query_llm("sys", "user", response_format="json")
        self.assertEqual(result, '{"queries": ["test1", "test2"]}')

    @patch('src.llm.client.chat.completions.create')
    def test_query_llm_failure(self, mock_create):
        mock_create.side_effect = Exception("API Error")
        result = query_llm("sys", "user")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
