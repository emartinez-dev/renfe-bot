from scraper.scraper import RenfeScraper
from scraper.utils import format_time
import time
import requests

import configparser

def prompt_credentials():
	config = configparser.ConfigParser()
	config.read("config.ini")

	if 'Telegram' not in config:
		config['Telegram'] = {}
	if 'secret_token' not in config['Telegram']:
		config['Telegram']['secret_token'] = input("Enter your Telegram bot secret token: ")
	if 'chat_id' not in config['Telegram']:
		config['Telegram']['chat_id'] = input("Enter your Telegram chat id: ")

	with open('config.ini', 'w') as configfile:
		config.write(configfile)

class Informer:
	def __init__(self, origin_station, destination_station, departure_date, return_date):
		self.origin_station = origin_station
		self.destination_station = destination_station
		self.departure_date = departure_date
		self.return_date = return_date
		self.scraper = RenfeScraper()
		self.data = None
		self.origin_ticket = None
		self.destination_ticket = None

	def loop(self, filter:dict=None):
		scraper = self.scraper
		scraper.find_trains(self.origin_station, self.destination_station, \
		    self.departure_date, self.return_date)
		origin_ticket = True
		destination_ticket = False
		while not origin_ticket or not destination_ticket:
			time.sleep(60)
			scraper.driver.refresh()
			scraper.get_results()
			if not origin_ticket:
				origin_ticket, self.origin_ticket = scraper.check_origin_ticket(filter)
				if origin_ticket:
					print(self.origin_ticket)
					self.notify("Origin tickets found!")
					self.notify(self.origin_ticket.to_string())
			if not destination_ticket:
				destination_ticket, self.destination_ticket = scraper.check_destination_ticket(filter)
				if destination_ticket:
					print(self.destination_ticket)
					self.notify("Destination tickets found!")
					self.notify(self.destination_ticket.to_string())

	def notify(self, message):
		url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
		requests.get(url).json()

origin_station = "Málaga María Zambrano"
destination_station = "Sevilla-Santa Justa"
departure_date = "19-07-2023 00:00"
return_date = "20-07-2023 00:00"

train_filter = {
	"max_price": 20,
	"max_duration": 4,
	"ida_earliest": format_time("08.00"),
	"ida_latest": format_time("16.00"),
	"vuelta_earliest": format_time("08.00"),
	"vuelta_latest": format_time("16.00"),
}

informer = Informer(origin_station, destination_station, departure_date, return_date)
informer.loop(train_filter)

