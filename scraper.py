from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parse_data import clear_dataframe, parse_table
from utils import str_to_dt, format_time

class RenfeScraper:

	def __init__(self):
		HOME_RENFE = "https://www.renfe.com/es/es"
		service_object = Service(binary_path)
		driver = webdriver.Chrome(service=service_object)
		driver.implicitly_wait(10)
		driver.get(HOME_RENFE)
		self.driver = driver
		self.train_data = []

	def find_trains(self, origin_name:str, destination_name:str, origin_date:str, destination_date:str):
		self.search_stations(origin_name, destination_name)
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
			raise Exception("You can't go back in time")

		# datepicker selectors
		DATE_OPEN_SELECTOR = "input#first-input"
		DELETE_BUTTON_SELECTOR = "button.lightpick__delete-action"
		APPLY_BUTTON_SELECTOR = "button.lightpick__apply-action-sub"
		SEARCH_BUTTON_SELECTOR = 'button[title="Buscar billete"]'

		# datepicker part
		self.find_and_click_with_retry(DATE_OPEN_SELECTOR)
		self.find_and_click_with_retry(DELETE_BUTTON_SELECTOR)
		self.find_and_click_with_retry(ts_origin_selector)
		self.find_and_click_with_retry(ts_destination_selector)
		# apply and search
		self.find_and_click_with_retry(APPLY_BUTTON_SELECTOR)
		self.find_and_click_with_retry(SEARCH_BUTTON_SELECTOR)
		# check if the trains page is correctly loaded
		wait = WebDriverWait(self.driver, 10)
		train_list_selector = "#listaTrenesTable"
		try:
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, train_list_selector)))
			print("Trains page loaded")
		except Exception:
			print("Trains page couldn't be loaded")

	def get_results(self):
		driver = self.driver
		actions = ActionChains(driver)
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#listaTrenesTBodyIda > tr")))
		element.click()
		vuelta_button = driver.find_element(By.CSS_SELECTOR, 'a[title="Trenes Trayecto Vuelta"]')
		actions.move_to_element(vuelta_button).click()
		actions.perform()
		element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#listaTrenesTBodyVuelta > tr")))
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		tbody_ida = soup.find("tbody", id="listaTrenesTBodyIda")
		tbody_vuelta = soup.find("tbody", id="listaTrenesTBodyVuelta")
		ida_trains = tbody_ida.find_all("tr", class_="trayectoRow")
		vuelta_trains = tbody_vuelta.find_all("tr", class_="trayectoRow")
		ida_data = parse_table(ida_trains, "ida")
		vuelta_data = parse_table(vuelta_trains, "vuelta")
		data = ida_data + vuelta_data
		self.train_data = data
		if len(data) == 0:
			raise Exception("No trains found")
		self.df = pd.DataFrame(data)
		self.df = clear_dataframe(self.df)

	def check_tickets(self, direction, earliest_key, latest_key, train_filter):
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
			return False, None
		print(f"{direction.capitalize()} tickets found")
		return True, tickets

	def check_origin_ticket(self, train_filter):
		return self.check_tickets('ida', 'ida_earliest', 'ida_latest', train_filter)

	def check_destination_ticket(self, train_filter):
		return self.check_tickets('vuelta', 'vuelta_earliest', 'vuelta_latest', train_filter)

	def find_and_click_with_retry(self, selector):
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
			except StaleElementReferenceException:
				num_retries += 1
				element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
