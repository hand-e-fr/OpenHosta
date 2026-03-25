import os
from unittest.mock import patch, mock_open
from OpenHosta.defaults import reload_dotenv, config

def test_reload_dotenv_success():
    """Test that reload_dotenv successfully loads environment variables."""
    # Mock the .env file content
    mock_env_content = "OPENHOSTA_DEFAULT_MODEL_NAME=test-model\nOPENHOSTA_DEFAULT_MODEL_API_KEY=test-key"
    
    # We use patch.dict to ensure os.environ is restored after the test
    with patch.dict(os.environ, {}, clear=False), \
         patch("os.path.isfile", return_value=True), \
         patch("builtins.open", mock_open(read_data=mock_env_content)):
        
        # Call reload_dotenv
        result = reload_dotenv()
        
        # Assert the function returns True (success)
        assert result is True
        
        # Assert environment variables are set
        assert os.getenv("OPENHOSTA_DEFAULT_MODEL_NAME") == "test-model"
        assert os.getenv("OPENHOSTA_DEFAULT_MODEL_API_KEY") == "test-key"
        
        # Assert config values are updated
        assert config.DefaultModel.model_name == "test-model"
        assert config.DefaultModel.api_key == "test-key"

def test_reload_dotenv_file_not_found():
    """Test reload_dotenv behavior when .env file is not found."""
    with patch("os.path.isfile", return_value=False):
        result = reload_dotenv(dotenv_path="./nonexistent.env")
        assert result is False

def test_reload_dotenv_override_behavior():
    """Test that override parameter controls environment variable overriding."""
    
    # Using patch.dict to isolate this test from the real environment
    with patch.dict(os.environ, {"OPENHOSTA_DEFAULT_MODEL_NAME": "original-value"}, clear=False):
        
        # Mock .env file with different value
        mock_env_content = "OPENHOSTA_DEFAULT_MODEL_NAME=new-value"
        
        with patch("os.path.isfile", return_value=True), \
             patch("builtins.open", mock_open(read_data=mock_env_content)):
            
            # Test with override=False (should not change existing variable)
            result = reload_dotenv(override=False)
            assert result is True
            assert os.getenv("OPENHOSTA_DEFAULT_MODEL_NAME") == "original-value"
            
            # Test with override=True (should change existing variable)
            result = reload_dotenv(override=True)
            assert result is True
            assert os.getenv("OPENHOSTA_DEFAULT_MODEL_NAME") == "new-value"

def test_dotenv_loading_in_parent_directories():
    """Test that reload_dotenv finds .env file in parent directories."""
    # Mock a hierarchy where .env is in a parent directory
    # Isolate environment with patch.dict
    with patch.dict(os.environ, {}, clear=False), \
         patch("os.path.isfile") as mock_isfile, \
         patch("builtins.open", mock_open(read_data="OPENHOSTA_DEFAULT_MODEL_NAME=parent-value")):
        
        # Configure isfile to return False for current path, True for parent
        def side_effect(path):
            return "parent" in path
        
        mock_isfile.side_effect = side_effect
        
        result = reload_dotenv(dotenv_path="./current/.env")
        assert result is True
        assert os.getenv("OPENHOSTA_DEFAULT_MODEL_NAME") == "parent-value"