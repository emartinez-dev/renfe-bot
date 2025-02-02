import pytest
from unittest.mock import patch, mock_open
from src.config import init_bot, get_bot_token

def test_get_bot_token_no_config():
    with patch("builtins.open", mock_open(read_data="")):
        with patch("src.config.init_bot") as mock_init_bot:
            with pytest.raises(KeyError):
                get_bot_token()
