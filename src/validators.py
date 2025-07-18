"""This module contains the validators for the user input"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import dateparser

from errors import StationNotFound
from messages import user_messages as msg
from models import StationRecord
from storage import StationsStorage


@dataclass
class StationValidationResult:
    """Holds the result of station validation"""

    is_valid: bool
    station: StationRecord | None = None
    error_message: str = ""

    def __bool__(self):
        return self.is_valid


@dataclass
class DateValidationResult:
    """Holds the result of date validation"""

    is_valid: bool
    date: datetime | None = None
    error_message: str = ""

    def __bool__(self):
        return self.is_valid

@dataclass
class FloatValidationResult:
    """Holds the result of a float number validation"""

    is_valid: bool
    number: float | None = None
    error_message: str = ""

    def __bool__(self):
        return self.is_valid


def validate_station(station_name: Optional[str]) -> StationValidationResult:
    """Validates the station provided by the user, returning partial matches if the station is
    not found"""
    if station_name is None:
        return StationValidationResult(is_valid=False, error_message=msg["station_invalid"])

    try:
        station = StationsStorage.get_station(station_name.upper())
        return StationValidationResult(is_valid=True, station=station)

    except StationNotFound:
        possible_stations = StationsStorage.find_station(station_name)
        error_message = (
            msg["station_not_found"].format(station_name,
                                            "\n".join(map(str.title, possible_stations)))
            if possible_stations
            else msg["station_invalid"]
        )
        return StationValidationResult(is_valid=False, error_message=error_message)


def validate_date(message: Optional[str]) -> DateValidationResult:
    """Validates the date provided by the user using the dateparser library, that supports
    creating a datetime object from a natural language string in multiple languages"""
    if not message:
        return DateValidationResult(is_valid=False, error_message=msg["wrong_date"])

    parsed_date = dateparser.parse(message,
                                   languages=["es", "en"],
                                   settings={"STRICT_PARSING": True})
    if parsed_date is None:
        return DateValidationResult(is_valid=False, error_message=msg["wrong_date"])
    return DateValidationResult(is_valid=True, date=parsed_date)


def validate_float(message: Optional[str]) -> FloatValidationResult:
    """Validates the float number provided by the user"""
    if not message:
        return FloatValidationResult(is_valid=False, error_message=msg["wrong_number"])
    parsed_number = float(message)
    return FloatValidationResult(is_valid=True, number=parsed_number)
