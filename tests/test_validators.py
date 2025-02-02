import pytest
from datetime import datetime
from dataclasses import dataclass
from validators import validate_station, validate_date, validate_float, StationValidationResult, DateValidationResult, FloatValidationResult
from errors import StationNotFound
from models import StationRecord
from storage import StationsStorage
from messages import user_messages as msg

@dataclass
class Message:
    text: str | None = None

@pytest.fixture
def mock_message():
    return Message()

def test_validate_station_valid(mock_message, mocker):
    mock_message.text = "Madrid"
    mock_station = StationRecord(name="Madrid", code="MAD")
    mocker.patch.object(StationsStorage, 'get_station', return_value=mock_station)
    
    result = validate_station(mock_message)
    
    assert result.is_valid
    assert result.station == mock_station
    assert result.error_message == ""

def test_validate_station_not_found(mock_message, mocker):
    mock_message.text = "Unknown"
    mocker.patch.object(StationsStorage, 'get_station', side_effect=StationNotFound)
    mocker.patch.object(StationsStorage, 'find_station', return_value=["Madrid", "Barcelona"])
    
    result = validate_station(mock_message)
    
    assert not result.is_valid
    assert result.station is None
    assert result.error_message == msg["station_not_found"].format("Unknown", "Madrid\nBarcelona")

def test_validate_station_no_text(mock_message):
    mock_message.text = None
    
    result = validate_station(mock_message)
    
    assert not result.is_valid
    assert result.station is None
    assert result.error_message == msg["station_invalid"]

def test_validate_date_valid(mock_message):
    mock_message.text = "Hoy a las 07:00"
    
    result = validate_date(mock_message)
    
    assert result.is_valid
    assert result.date == datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
    assert result.error_message == ""

def test_validate_date_invalid(mock_message):
    mock_message.text = "invalid date"
    
    result = validate_date(mock_message)
    
    assert not result.is_valid
    assert result.date is None
    assert result.error_message == msg["wrong_date"]

def test_validate_date_no_text(mock_message):
    mock_message.text = None
    
    result = validate_date(mock_message)
    
    assert not result.is_valid
    assert result.date is None
    assert result.error_message == msg["wrong_date"]

def test_validate_float_valid(mock_message):
    mock_message.text = "123.45"
    
    result = validate_float(mock_message)
    
    assert result.is_valid
    assert result.number == 123.45
    assert result.error_message == ""

def test_validate_float_invalid(mock_message):
    mock_message.text = "invalid number"
    
    with pytest.raises(ValueError):
        validate_float(mock_message)

def test_validate_float_no_text(mock_message):
    mock_message.text = None
    
    result = validate_float(mock_message)
    
    assert not result.is_valid
    assert result.number is None
    assert result.error_message == msg["wrong_number"]
