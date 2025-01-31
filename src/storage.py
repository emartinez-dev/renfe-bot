import itertools
import json
from pathlib import Path
from typing import Any, Dict, List, Iterable, Optional

from thefuzz import process

from errors import StationNotFound
from models import StationRecord

STATIONS_PATH = Path("assets/stations.json")


def load_json(path: Path) -> Dict[str, Any]:
    """Read a JSON from a given path and return it's content as a dict

    :param path: Where the JSON file is located
    :type path: str
    :return: JSON contents
    :rtype: Dict[str, Any]
    """

    with open(path, "r", encoding="utf-8") as f:
        json_content = json.load(f)
    return json_content


class StationsStorage:
    """Manages the storage and retrieval of station data.

    :param stations: A dictionary containing station data, where the key is the station name and the
                     value is a dictionary with station details.
    :type stations: Dict, optional
    """

    stations: Optional[Dict[str, Dict]] = None

    @classmethod
    def get_station(cls, name: str) -> StationRecord:
        """Retrieves a station record by its name

        :param name: The name of the station to retrieve
        :type name: str
        :raises StationNotFound: If the station is not found in the storage.
        :return: The record of the requested station, containing its name and code
        :rtype: StationRecord
        """

        if cls.stations is None:
            cls.stations = load_json(STATIONS_PATH)

        if (station := cls.stations.get(name, None)) is None:
            raise StationNotFound(f"Couldn't find the station '{name}'")

        assert isinstance(station, dict)
        return StationRecord(name=station['desgEstacion'], code=station['clave'])

    @classmethod
    def find_station(cls, name: str) -> List[str]:
        """Retrieves a list of station records fuzzy finding the names

        :param name: The name of the station to retrieve
        :type name: str
        :raises StationNotFound: If the station is not found in the storage.
        :return: The names of similar stations, containing its name and code
        :rtype: strings
        """

        if cls.stations is None:
            cls.stations = load_json(STATIONS_PATH)

        guesses = process.extractBests(name, cls.stations.keys(), score_cutoff=90)
        return [guess[0] for guess in guesses]

    @classmethod
    def get_all_stations(cls) -> Iterable[StationRecord]:
        """Retrieves all available stations.

        If the station data is not loaded, it initializes the storage by
        loading data from a JSON file.

        :return: A consumable iterable containing the records for all stations.
        :rtype: Iterable[StationRecord]
        """
        if cls.stations is None:
            cls.stations = load_json(STATIONS_PATH)

        return itertools.chain([StationRecord(name=station['desgEstacion'], code=station['clave'])
                                for _, station in cls.stations.items()])
