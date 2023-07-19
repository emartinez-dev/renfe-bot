import logging
import os
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException,
                                        WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import scraper.exceptions as e
from scraper.parser import clear_dataframe, parse_table
from scraper.utils import str_to_dt

if not os.path.exists('logs'):
	os.makedirs('logs')

logfile = datetime.now().strftime('scraper_%H_%M_%d_%m_%Y.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f'logs/{logfile}', mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class RenfeScraper:
	"""
	Scraper for the Renfe website. It uses Selenium to interact with the page.

	The steps that the scraper follows are:
	1. Go to the Renfe home page
	2. Search for the origin and destination stations
	3. Search for the departure and return dates

	This part could be looped until the tickets are found
		4. Wait for the results page to load
		5. Parse the results page
		6. Filter the results according to the given filter

	"""

	def __init__(self):
		HOME_RENFE = "https://www.renfe.com/es/es"
		service_object = Service(binary_path)
		driver = webdriver.Chrome(service=service_object)
		self.driver = driver
		driver.implicitly_wait(10)
		search_selector = "div.rf-search__root"
		try:
			driver.get(HOME_RENFE)
			self._wait_for_element(search_selector)
			logger.info("Renfe page loaded")
		except WebDriverException:
			logger.error(f"Error loading Renfe page")
		self.df = None

	def find_trains(self, origin_name:str, destination_name:str, origin_date:str, destination_date:str):
		logger.info(f"Stations: {origin_name} -> {destination_name}")
		self.search_stations(origin_name, destination_name)
		logger.info(f"Date: {origin_date} - {destination_date}")
		self.search_dates(origin_date, destination_date)

	def search_stations(self, origin_name:str, destination_name:str):
		ORIGIN_SELECTOR = "input#origin"
		DESTINATION_SELECTOR = "input#destination"

		driver = self.driver
		actions = ActionChains(driver)
		origin_element = driver.find_element(By.CSS_SELECTOR, ORIGIN_SELECTOR)
		actions.move_to_element(origin_element).click()
		actions.send_keys(origin_name)
		actions.send_keys(Keys.ARROW_DOWN)
		actions.send_keys(Keys.RETURN)
		actions.perform()

		actions = ActionChains(driver)
		destination_element = driver.find_element(By.CSS_SELECTOR, DESTINATION_SELECTOR)
		actions.move_to_element(destination_element).click()
		actions.send_keys(destination_name)
		actions.send_keys(Keys.ARROW_DOWN)
		actions.send_keys(Keys.RETURN)
		actions.perform()

	def search_dates(self, origin_date:str, destination_date:str):
		# date format: "DD-MM-YYYY HH:MM"
		dt_origin = str_to_dt(origin_date)
		dt_destination = str_to_dt(destination_date)
		dt_yesterday = datetime.now() - timedelta(days=1)

		# the datepicker accepts timestamps in milliseconds
		ts_origin = int(dt_origin.timestamp()) * 1000
		ts_destination = int(dt_destination.timestamp()) * 1000
		ts_origin_selector = f'div[data-time="{ts_origin}"]'
		ts_destination_selector = f'div[data-time="{ts_destination}"]'

		# this check should be done before even starting the scraper
		if ts_destination < ts_origin or dt_origin < dt_yesterday:
			logger.error("Invalid date")
			raise e.InvalidDate("You can't go back in time")

		# datepicker selectors
		DATE_OPEN_SELECTOR = "input#first-input"
		DELETE_BUTTON_SELECTOR = "button.lightpick__delete-action"
		APPLY_BUTTON_SELECTOR = "button.lightpick__apply-action-sub"
		SEARCH_BUTTON_SELECTOR = 'button[title="Buscar billete"]'

		# datepicker part
		self._find_and_click_with_retry(DATE_OPEN_SELECTOR)
		self._find_and_click_with_retry(DELETE_BUTTON_SELECTOR)
		self._find_and_click_with_retry(ts_origin_selector)
		self._find_and_click_with_retry(ts_destination_selector)
		# apply and search
		self._find_and_click_with_retry(APPLY_BUTTON_SELECTOR)
		self._find_and_click_with_retry(SEARCH_BUTTON_SELECTOR)
		# check if the trains page is correctly loaded
		train_list_selector = "#listaTrenesTable"
		try:
			self._wait_for_element(train_list_selector)
		except:
			logger.error("Trains page couldn't be loaded")
			raise e.SearchFailed("Trains page couldn't be loaded")
		logger.info("Trains page loaded")

	def get_results(self):
		driver = self.driver
		# load both train tables
		ida_table_selector = "#listaTrenesTBodyIda > tr"
		vuelta_link_selector = 'a[title="Trenes Trayecto Vuelta"]'
		vuelta_table_selector = "#listaTrenesTBodyVuelta > tr"
		self._wait_for_element(ida_table_selector)
		self._find_and_click_with_retry(vuelta_link_selector)
		self._wait_for_element(vuelta_table_selector)
		# parse the tables
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		tbody_ida = soup.find("tbody", id="listaTrenesTBodyIda")
		tbody_vuelta = soup.find("tbody", id="listaTrenesTBodyVuelta")
		ida_trains = tbody_ida.find_all("tr", class_="trayectoRow")
		vuelta_trains = tbody_vuelta.find_all("tr", class_="trayectoRow")
		ida_data = parse_table(ida_trains, "ida")
		vuelta_data = parse_table(vuelta_trains, "vuelta")
		data = ida_data + vuelta_data
		if len(data) == 0:
			logger.error("No trains found")
			raise e.SearchFailed("No trains found")
		self.df = pd.DataFrame(data)
		self.df = clear_dataframe(self.df)

	def filter_results(self, direction, earliest_key, latest_key, train_filter):
		df = self.df
		tickets = df[df['direction'] == direction]
		tickets = tickets[tickets['status'] == 'available']
		if train_filter is not None:
			if 'train_type' in train_filter:
				tickets = tickets[tickets['train_type'] == train_filter['train_type']]
			if 'max_price' in train_filter:
				tickets = tickets[tickets['price'] <= train_filter['max_price']]
			if 'max_duration' in train_filter:
				tickets = tickets[tickets['duration'] <= train_filter['max_duration']]
			if earliest_key in train_filter:
				tickets = tickets[tickets['time_of_departure'] >= train_filter[earliest_key]]
			if latest_key in train_filter:
				tickets = tickets[tickets['time_of_departure'] <= train_filter[latest_key]]
		if len(tickets) == 0:
			logger.debug(f"No {direction} tickets found. Filter: {train_filter}")
			return False, None
		return True, tickets

	def check_origin_ticket(self, train_filter):
		return self.filter_results('ida', 'ida_earliest', 'ida_latest', train_filter)

	def check_destination_ticket(self, train_filter):
		return self.filter_results('vuelta', 'vuelta_earliest', 'vuelta_latest', train_filter)

	def _find_and_click_with_retry(self, selector):
		MAX_RETRIES = 3
		driver = self.driver
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
		actions = ActionChains(driver)
		num_retries = 0
		while num_retries < MAX_RETRIES:
			try:
				actions.move_to_element(element).click()
				actions.perform()
				break
			except:
				num_retries += 1
				element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
		if num_retries == MAX_RETRIES:
			logger.error(f"Max retries exceeded for selector {selector}")
			raise e.MaxRetriesExceeded(f"Max retries exceeded for selector {selector}")


	def _wait_for_element(self, selector):
		wait = WebDriverWait(self.driver, 10)
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
		if self.driver.find_elements(By.CSS_SELECTOR, selector) == []:
			logger.error(f"Element with selector {selector} not found")
			raise e.ElementNotFound(f"Element with selector {selector} not found")
