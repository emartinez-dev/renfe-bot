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

from constants import *
from parse_data import clear_dataframe, parse_table
from utils import convert_date_string, format_time


class RenfeScraper:
	def __init__(self):
		service_object = Service(binary_path)
		driver = webdriver.Chrome(service=service_object)
		driver.implicitly_wait(10)
		driver.get(HOME_RENFE)
		self.driver = driver
		self.train_data = []

	def search_stations(self, origin_name:str, destination_name:str):
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
		driver = self.driver
		datetime_origin = convert_date_string(origin_date)
		datetime_destination = convert_date_string(destination_date)
		datetime_yesterday = datetime.now() - timedelta(days=1)
		ts_origin = int(datetime_origin.timestamp()) * 1000
		ts_destination = int(datetime_destination.timestamp()) * 1000
		if ts_destination < ts_origin or datetime_origin < datetime_yesterday:
			raise Exception("You can't go back in time")
		actions = ActionChains(driver)
		open_date_element = driver.find_element(By.CSS_SELECTOR, OPEN_DATE_SELECTOR)
		actions.move_to_element(open_date_element).click()
		actions.perform()

		actions = ActionChains(driver)
		wait = WebDriverWait(driver, 10)
		delete_css = "button.lightpick__delete-action"
		delete_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, delete_css)))

		actions.move_to_element(delete_button).click()
		actions.perform()

		element1 = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[data-time="{ts_origin}"]')))
		actions = ActionChains(driver)
		max_retries = 3
		num_retries = 0
		while num_retries < max_retries:
			try:
				actions.move_to_element(element1).click()
				actions.perform()
				break
			except StaleElementReferenceException:
				num_retries += 1
				element1 = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[data-time="{ts_origin}"]')))

		element2 = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[data-time="{ts_destination}"]')))

		actions = ActionChains(driver)
		max_retries = 3
		num_retries = 0
		while num_retries < max_retries:
				try:
					actions.move_to_element(element2).click()
					actions.perform()
					break
				except StaleElementReferenceException:
					num_retries += 1
					element2 = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[data-time="{ts_destination}"]')))

		button_css = "button.lightpick__apply-action-sub"
		search_css = 'button[title="Buscar billete"]'

		actions = ActionChains(driver)
		apply_button = driver.find_element(By.CSS_SELECTOR, button_css)
		submit_button = driver.find_element(By.CSS_SELECTOR, search_css)
		actions.move_to_element(apply_button).click()
		actions.move_to_element(submit_button).click()
		actions.perform()

	def get_results(self):
		driver = self.driver
		assert "Lista de Trenes" in driver.title
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

	def check_origin_ticket(self, train_filter):
		df = self.df
		tickets = df[df['direction'] == 'ida']
		tickets = tickets[tickets['status'] == 'available']
		if train_filter is not None:
			if 'train_type' in train_filter:
				tickets = tickets[tickets['train_type'] == train_filter['train_type']]
			if 'max_price' in train_filter:
				tickets = tickets[tickets['price'] <= train_filter['max_price']]
			if 'max_duration' in train_filter:
				tickets = tickets[tickets['duration'] <= train_filter['max_duration']]
			if 'ida_earliest' in train_filter:
				tickets = tickets[tickets['time_of_departure'] >= train_filter['ida_earliest']]
			if 'ida_latest' in train_filter:
				tickets = tickets[tickets['time_of_departure'] <= train_filter['ida_latest']]
		if len(tickets) == 0:
			return False, None
		print("Origin tickets found")
		return True, tickets

	def check_destination_ticket(self, train_filter):
		df = self.df
		tickets = df[df['direction'] == 'vuelta']
		tickets = tickets[tickets['status'] == 'available']
		if train_filter is not None:
			if 'train_type' in train_filter:
				tickets = tickets[tickets['train_type'] == train_filter['train_type']]
			if 'max_price' in train_filter:
				tickets = tickets[tickets['price'] <= train_filter['max_price']]
			if 'max_duration' in train_filter:
				tickets = tickets[tickets['duration'] <= train_filter['max_duration']]
			if 'ida_earliest' in train_filter:
				tickets = tickets[tickets['time_of_departure'] >= train_filter['vuelta_earliest']]
			if 'ida_latest' in train_filter:
				tickets = tickets[tickets['time_of_departure'] <= train_filter['vuelta_latest']]
		if len(tickets) == 0:
			return False, None
		print("Destination tickets found")
		return True, tickets


