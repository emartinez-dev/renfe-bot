import pytest
from datetime import datetime, time
from unittest.mock import patch
from errors import InvalidTrainRideFilter
from models import TrainRideRecord, TrainRideFilter, StationRecord


@pytest.fixture
def sample_rides():
    return [
        TrainRideRecord(
            origin="Madrid",
            destination="Barcelona",
            departure_time=datetime(2025, 1, 30, 8, 30),
            arrival_time=datetime(2025, 1, 30, 11, 30),
            duration=180,
            price=50.0,
            available=True,
            train_type="AVE"
        ),
        TrainRideRecord(
            origin="Madrid",
            destination="Barcelona",
            departure_time=datetime(2025, 1, 30, 9, 30),
            arrival_time=datetime(2025, 1, 30, 12, 30),
            duration=180,
            price=55.0,
            available=False,
            train_type="ALVIA"
        ),
        TrainRideRecord(
            origin="Madrid",
            destination="Barcelona",
            departure_time=datetime(2025, 1, 30, 10, 30),
            arrival_time=datetime(2025, 1, 30, 13, 30),
            duration=180,
            price=60.0,
            available=True,
            train_type="ALVIA"
        )
    ]


def test_filter_rides_origin_and_destination(sample_rides):
    filter = TrainRideFilter(
        origin="Madrid",
        destination="Barcelona",
        departure_date=datetime(2025, 1, 30),
        max_duration_minutes=None,
        max_price=None
    )

    result = filter.filter_rides(sample_rides)

    assert len(result) == 2  # Only 2 available rides


def test_filter_rides_by_min_departure_hour(sample_rides):
    filter = TrainRideFilter(
        origin="Madrid",
        destination="Barcelona",
        departure_date=datetime(2025, 1, 30, 9, 0),
        max_duration_minutes=None,
        max_price=None
    )

    result = filter.filter_rides(sample_rides)

    assert len(result) == 1  # Only the third ride should pass


def test_filter_rides_by_max_duration(sample_rides):
    filter = TrainRideFilter(
        origin="Madrid",
        destination="Barcelona",
        departure_date=datetime(2025, 1, 30),
        max_duration_minutes=180,
        max_price=None
    )

    result = filter.filter_rides(sample_rides)

    assert len(result) == 2  # All rides are within the duration limit


def test_filter_rides_by_max_price(sample_rides):
    filter = TrainRideFilter(
        origin="Madrid",
        destination="Barcelona",
        departure_date=datetime(2025, 1, 30),
        max_duration_minutes=None,
        max_price=55.0
    )

    result = filter.filter_rides(sample_rides)

    assert len(result) == 1  # Only the first ride should pass due to price


def test_filter_rides_no_results(sample_rides):
    filter = TrainRideFilter(
        origin="Madrid",
        destination="Barcelona",
        departure_date=datetime(2025, 1, 31),  # Different date
        max_duration_minutes=1,
        max_price=None
    )

    with pytest.raises(InvalidTrainRideFilter):
        filter.filter_rides(sample_rides)


def test_train_ride_str(sample_rides):
    ride = sample_rides[0]
    expected_str = "🚆 Tren AVE: 🕒 08:30 - 11:30 🕙 - 50.00 €\n"
    assert str(ride) == expected_str
