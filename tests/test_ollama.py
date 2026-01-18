import pytest
from unittest.mock import patch, MagicMock
from OpenHosta.models import OllamaModel, ModelCapabilities
import json

class TestOllamaModel:
    @pytest.fixture
    def model(self):
        return OllamaModel(model_name="test-model", base_url="http://test:11434")

    @patch('requests.post')
    def test_api_call_structure(self, mock_post, model):
        # Mock successful response from Ollama /api/generate
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Hello world",
            "prompt_eval_count": 10,
            "eval_count": 5,
            "logprobs": [0.1, 0.2]
        }
        mock_post.return_value = mock_response

        messages = [
            {"role": "user", "content": [
                {"type": "text", "text": "Hello"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KG..."}}
            ]}
        ]
        
        response = model.api_call(messages, llm_args={"temperature": 0.7, "force_json_output": True})

        # Verify request body
        args, kwargs = mock_post.call_args
        body = kwargs['json']
        
        assert body['model'] == "test-model"
        assert body['prompt'] == "Hello"
        assert body['images'] == ["iVBORw0KG..."]
        assert body['temperature'] == 0.7
        assert body['format'] == "json"
        assert body['stream'] is False

        # Verify internal response format
        assert response['choices'][0]['message']['content'] == "Hello world"
        assert response['usage']['total_tokens'] == 15

    @patch('requests.post')
    def test_embedding_api_call(self, mock_post, model):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        mock_post.return_value = mock_response

        embeddings = model.embedding_api_call(["text1", "text2"])

        # Verify request body
        args, kwargs = mock_post.call_args
        body = kwargs['json']
        assert body['input'] == ["text1", "text2"]
        assert body['model'] == "test-model"

        # Verify result
        assert embeddings == [[0.1, 0.2], [0.3, 0.4]]

    @patch('requests.post')
    def test_api_call_error_handling(self, mock_post, model):
        from OpenHosta.core.errors import RateLimitError, ApiKeyError
        
        # Test 429
        mock_post.return_value.status_code = 429
        with pytest.raises(RateLimitError):
            model.api_call([])

        # Test 401
        mock_post.return_value.status_code = 401
        with pytest.raises(ApiKeyError):
            model.api_call([])
