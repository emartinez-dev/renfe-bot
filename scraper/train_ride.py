import Levenshtein
from datetime import datetime, timedelta


class TrainQuery:
    def __init__(self, origin, destination, departure, arrival, round_trip):
        self.origin = sanitize_station_input(origin)
        self.destination = sanitize_station_input(destination)
        self.departure = str_to_dt(departure)
        self.arrival = str_to_dt(arrival)
        self.round_trip = round_trip

        yesterday = datetime.now() - timedelta(days=1)

        if self.arrival > self.departure:
            raise ValueError("Departure should be before arrival")
        if self.departure < yesterday:
            raise ValueError("Departure should be today or later")
        if self.origin is None:
            raise ValueError("Origin station is not recognized")
        if self.destination is None:
            raise ValueError("Destination station is not recognized")


class TrainRide:
    def __init__(self, origin, destination, departure, arrival):
        self.origin = origin
        self.destination = destination
        self.date = 0
        self.price = 0
        self.duration = 0
        # date format: "DD-MM-YYYY HH:MM"
        return


def sanitize_station_input(_input):
    with open('resources/stations.txt', 'r') as f:
        stations = [line.strip() for line in f]

    clean_input = _input.upper().strip()
    closest_station = None
    closest_distance = 100

    for station in stations:
        distance = Levenshtein.distance(clean_input, station)
        if distance < closest_distance:
            closest_station = station
            closest_distance = distance

    if closest_distance > 2:
        return None
    return closest_station


def str_to_dt(dt_str):
    dt_format = "%d-%m-%Y %H:%M"
    try:
        dt = datetime.strptime(dt_str, dt_format)
    except ValueError:
        dt = datetime.strptime(dt_str + " 00:00", dt_format)
    return dt
