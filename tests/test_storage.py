import json
import pytest
from unittest.mock import patch, mock_open
from thefuzz import process
from errors import StationNotFound
from storage import StationsStorage, load_json, STATIONS_PATH


# Sample data for testing
mock_stations_data = {
    "Madrid": {"desgEstacion": "Madrid", "clave": "1234"},
    "Barcelona": {"desgEstacion": "Barcelona", "clave": "5678"},
    "Sevilla": {"desgEstacion": "Sevilla", "clave": "91011"}
}

# Test for the load_json function
def test_load_json():
    with patch("storage.open", mock_open(read_data='{"Madrid": {"desgEstacion": "Madrid", "clave": "1234"}}')):
        result = load_json(STATIONS_PATH)
        assert result == {"Madrid": {"desgEstacion": "Madrid", "clave": "1234"}}


# Test for get_station
def test_get_station():
    # Patch load_json to return mock data
    with patch("storage.load_json", return_value=mock_stations_data):
        station = StationsStorage.get_station("Madrid")
        assert station.name == "Madrid"
        assert station.code == "1234"


# Test for get_station when the station is not found
def test_get_station_not_found():
    with patch("storage.load_json", return_value=mock_stations_data):
        with pytest.raises(StationNotFound):
            StationsStorage.get_station("NonExistentStation")


# Test for find_station with fuzzy matching
def test_find_station():
    # Patch load_json and extractBests to simulate fuzzy matching
    with patch("storage.load_json", return_value=mock_stations_data):
        with patch.object(process, 'extractBests', return_value=[("Madrid", 95)]):
            result = StationsStorage.find_station("Madird")
            assert result == ["Madrid"]


# Test for get_all_stations
def test_get_all_stations():
    # Patch load_json to return mock data
    with patch("storage.load_json", return_value=mock_stations_data):
        all_stations = list(StationsStorage.get_all_stations())
        assert len(all_stations) == 3
        assert all_stations[0].name == "Madrid"
        assert all_stations[1].name == "Barcelona"
        assert all_stations[2].name == "Sevilla"


# Test for get_all_stations with empty storage
def test_get_all_stations_empty():
    with patch("storage.load_json", return_value={}):
        StationsStorage.stations = None # Reset the stations data so it's clean
        all_stations = list(StationsStorage.get_all_stations())
        assert len(all_stations) == 0


# Test for loading invalid JSON (simulate an error in JSON file)
def test_load_json_invalid():
    with patch("storage.open", mock_open(read_data="invalid json")):
        with pytest.raises(json.JSONDecodeError):
            load_json(STATIONS_PATH)

