from scraper.scraper import RenfeScraper, RenfeData

import time
import os
import sys

MINIMAL_FILTER = {
    "origin_departure_time": "00.00",
    "origin_arrival_time": "23.59",
    "return_departure_time": "00.00",
    "return_arrival_time": "23.59",
    "max_price": 1000,
}


class Watcher:
    def __init__(self, renfe_data: RenfeData, filter: dict = MINIMAL_FILTER):
        self.query = renfe_data
        self.scraper = RenfeScraper()
        self.scraper.find_trains(self.query)
        self.oneway = False if renfe_data.return_date != "" else True
        self.departure_tickets = []
        self.return_tickets = []
        self.filter = filter
        self.fill_filter()

    def fill_filter(self):
        if "origin_departure_time" not in self.filter.keys():
            self.filter["origin_departure_time"] = MINIMAL_FILTER["origin_departure_time"]
        if "origin_arrival_time" not in self.filter.keys():
            self.filter["origin_arrival_time"] = MINIMAL_FILTER["origin_arrival_time"]
        if "return_departure_time" not in self.filter.keys():
            self.filter["return_departure_time"] = MINIMAL_FILTER["return_departure_time"]
        if "return_arrival_time" not in self.filter.keys():
            self.filter["return_arrival_time"] = MINIMAL_FILTER["return_arrival_time"]
        if "max_price" not in self.filter.keys():
            self.filter["max_price"] = MINIMAL_FILTER["max_price"]

    def loop(self):
        found_departure = False
        found_return = True if self.oneway else False
        while not found_departure or not found_return:
            trains = self.scraper.get_results()
            if len(trains) == 0:
                return
            if not found_departure:
                try:
                    self.departure_tickets = self.check_filters(trains, "ida")
                    found_departure = True
                except Exception as e:
                    print(e)
                    found_departure = True
            if not found_return:
                try:
                    self.return_tickets = self.check_filters(trains, "vuelta")
                    found_return = True
                except Exception as e:
                    print(e)
                    found_return = True
            if found_departure and found_return:
                self.scraper.stop()
            else:
                self.scraper.wait_and_refresh(30)

    def get_tickets(self):
        return self.departure_tickets, self.return_tickets

    def check_filters(self, trains, way):
        valid_trains = []
        for train in trains:
            if train["direction"] == way and way == "ida":
                if train["departure"] >= self.filter["origin_departure_time"] \
                        and train["arrival"] <= self.filter["origin_arrival_time"] \
                        and train["price"] <= self.filter["max_price"]:
                    valid_trains.append(train)
            elif train["direction"] == way and way == "vuelta":
                if train["departure"] >= self.filter["return_departure_time"] \
                        and train["arrival"] <= self.filter["return_arrival_time"] \
                        and train["price"] <= self.filter["max_price"]:
                    valid_trains.append(train)
        if len(valid_trains) == 0:
            raise Exception("No valid trains for the given filters")
        available_trains = [train for train in valid_trains if train["status"] == "available"]
        return available_trains
