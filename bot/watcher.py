import time
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from scraper.scraper import RenfeScraper
from scraper.utils import format_time

class Watcher:
	def __init__(self, origin_station, destination_station, departure_date, return_date):
		self.origin_station = origin_station
		self.destination_station = destination_station
		self.departure_date = departure_date
		self.return_date = return_date
		self.scraper = RenfeScraper()
		self.data = None
		self.tickets_ida = None
		self.tickets_vuelta = None

	def loop(self, filter:dict=None):
		found_ida = False
		found_vuelta = False
		if filter["return"] == False:
			found_vuelta = True
		scraper = self.scraper
		scraper.find_trains(self.origin_station, self.destination_station, \
		    self.departure_date, self.return_date)
		while not found_ida or not found_vuelta:
			time.sleep(60)
			scraper.driver.refresh()
			scraper.get_results()
			if not found_ida:
				found_ida, self.tickets_ida = scraper.check_origin_ticket(filter)
				if found_ida:
					print(self.tickets_ida)
			if not found_vuelta:
				found_vuelta, self.tickets_vuelta = scraper.check_destination_ticket(filter)
				if found_vuelta:
					print(self.tickets_vuelta)
		scraper.driver.quit()
		return self.tickets_ida, self.tickets_vuelta
