import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.scraper import Scraper, extract_dwr_token, extract_train_list, create_search_id, create_session_script_id, tokenify
from models import StationRecord, TrainRideRecord
from errors import InvalidDWRToken, InvalidTrainRideFilter

@pytest.fixture
def scraper():
    origin = StationRecord(name="Madrid", code="MAD")
    destination = StationRecord(name="Barcelona", code="BCN")
    departure_date = datetime(2023, 12, 25)
    return Scraper(origin, destination, departure_date)

def test_create_search_id():
    search_id = create_search_id()
    assert len(search_id) == 5
    assert search_id.startswith("_")

def test_create_session_script_id():
    dwr_token = "test_token"
    session_script_id = create_session_script_id(dwr_token)
    assert session_script_id.startswith(dwr_token)

def test_tokenify():
    number = 123456
    token = tokenify(number)
    assert isinstance(token, str)

def test_extract_dwr_token():
    response_text = 'r.handleCallback("0","0","test_token")'
    token = extract_dwr_token(response_text)
    assert token == "test_token"

def test_extract_dwr_token_invalid():
    response_text = 'invalid response'
    with pytest.raises(InvalidDWRToken):
        extract_dwr_token(response_text)

def test_extract_train_list():
    response_text = 'r.handleCallback(0,0,{"listadoTrenes":[]});'
    train_list = extract_train_list(response_text)
    assert "listadoTrenes" in train_list

def test_invalid_return_date():
    origin = StationRecord(name="Madrid", code="MAD")
    destination = StationRecord(name="Barcelona", code="BCN")
    departure_date = datetime(2023, 12, 25)
    return_date = datetime(2023, 12, 24)
    with pytest.raises(InvalidTrainRideFilter):
        Scraper(origin, destination, departure_date, return_date)

@patch('src.scraper.requests.Session.post')
def test_do_search(mock_post, scraper):
    mock_post.return_value.ok = True
    scraper._do_search()
    assert mock_post.called

@patch('src.scraper.requests.Session.post')
def test_do_get_dwr_token(mock_post, scraper):
    mock_post.return_value.ok = True
    mock_post.return_value.text = 'r.handleCallback("0","0","test_token")'
    scraper._do_get_dwr_token()
    assert scraper.dwr_token == "test_token"

@patch('src.scraper.requests.Session.post')
def test_do_update_session_objects(mock_post, scraper):
    mock_post.return_value.ok = True
    scraper.dwr_token = "test_token"
    scraper.script_session_id = "test_script_session_id"
    scraper._do_update_session_objects()
    assert mock_post.called

@patch('src.scraper.requests.Session.post')
def test_do_get_train_list(mock_post, scraper):
    mock_post.return_value.ok = True
    mock_post.return_value.text = 'r.handleCallback(0,0,{"listadoTrenes":[]});'
    train_list = scraper._do_get_train_list()
    assert "listadoTrenes" in train_list

def test_change_datetime_hour():
    date = datetime(2023, 12, 25)
    hour = "14:30"
    new_date = Scraper._change_datetime_hour(hour, date)
    assert new_date.hour == 14
    assert new_date.minute == 30

def test_is_train_available():
    train = {
        "completo": False,
        "razonNoDisponible": "",
        "tarifaMinima": "10.00"
    }
    assert Scraper._is_train_available(train)

def test_is_train_not_available():
    train = {
        "completo": True,
        "razonNoDisponible": "1",
        "tarifaMinima": None
    }
    assert not Scraper._is_train_available(train)
