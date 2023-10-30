from playwright.sync_api import sync_playwright
from calmjs.parse import es5
from calmjs.parse.unparsers.extractor import ast_to_dict
from urllib.parse import urlencode, quote
import time
import random
import string
import os
from inspect import cleandoc
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "\
             "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
RENFE_SEARCH_URL = "https://venta.renfe.com/vol/search.do"
RENFE_HOME = "https://www.renfe.com/es/es"
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Dnt": "1",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class RenfeData:
    def __init__(self, date_go: str, date_back: str, origin: str, destination: str):
        """

        format for date: dd/mm/yyyy
        date for back can be an empty string

        examples:
            desOrigen: SEVILLA-SANTA JUSTA
            desDestino: POSADAS
            cdgoOrigen: 0071,51003,51003
            cdgoDestino: 0071,50504,50504
        """

        STATIONS_LIST = self.get_stations_list()
        origin = self.find_station(STATIONS_LIST, origin)
        destination = self.find_station(STATIONS_LIST, destination)
        if origin is None or destination is None:
            raise Exception("Origin or destination not found")
        self.date_go = date_go
        self.date_back = date_back
        self.origin_code = origin[0]
        self.destination_code = destination[0]
        self.origin = origin[1]
        self.destination = destination[1]
        self.data = {
            "tipoBusqueda": "autocomplete",
            "currenLocation": "menuBusqueda",
            "vengoderenfecom": "SI",
            "cdgoOrigen": self.origin_code,
            "cdgoDestino": self.destination_code,
            "idiomaBusqueda": "ES",
            "FechaIdaSel": self.date_go,
            "FechaVueltaSel": self.date_back,
            "desOrigen": self.origin,
            "desDestino": self.destination,
            "_fechaIdaVisual": self.date_go,
            "_fechaVueltaVisual": self.date_back,
            "adultos_": "1",
            "ninos_": "0",
            "ninosMenores": "0",
            "numJoven": "",
            "numDorada": "",
            "codPromocional": "",
            "plazaH": "false",
            "Idioma": "es",
            "Pais": "ES"
        }

    def get_post_data(self):
        return self.data

    def get_cookies_from_data(self):
        data = self.data
        origin_code = data["cdgoOrigen"]
        origin_name = data["desOrigen"]
        destination_code = data["cdgoDestino"]
        destination_name = data["desDestino"]
        return (f'{{"origen":{{"code":"{origin_code}","name":"{origin_name}"}},'
                f'"destino":{{"code":"{destination_code}","name":"{destination_name}"}},'
                '"pasajerosAdultos":1,"pasajerosNinos":0,"pasajerosSpChild":0}}')

    def get_stations_list(self):
        """
        stations = get_stations_list()
        if stations is not None:
            for i in stations[:10]:
                print(i["desgEstacion"])
        """
        filename = "estacionesEstaticas.js"
        if not os.path.exists(filename):
            print("Downloading stations list")
            response = requests.get(URL_STATIONS)
            if response.status_code != 200:
                return None
            with open(filename, "w+") as f:
                f.write(response.text)

        with open(filename, "r") as f:
            file_content = f.read()
            stations = es5(file_content)
            stations_dict = ast_to_dict(stations)

        if "estacionesEstatico" in stations_dict:
            return stations_dict["estacionesEstatico"]
        return None

    def find_station(self, stations: list, station_name: str):
        for station in stations:
            if station["desgEstacion"] == station_name:
                return (station["clave"], station["desgEstacion"])
        return None


ride_data = RenfeData("02/11/2023", "03/11/2023", "POSADAS", "SEVILLA-SANTA JUSTA")

with sync_playwright() as p:
    # create a new browser instance
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(user_agent=USER_AGENT)
    page = context.new_page()
    page.goto(RENFE_HOME)

    # fill the data
    page.get_by_title("Buscar billete").evaluate("button => button.removeAttribute('disabled')")
    page.locator("#destination").click()
    for k, v in ride_data.get_post_data().items():
        page.evaluate('''object => {
            const element = document.querySelector(object.selector);
            if (element) {
                element.value = object.value;
            }
        }''', {"selector": f'[name="{k}"]', "value": v})
    page.click("text=Buscar billete")
    browser.close()
