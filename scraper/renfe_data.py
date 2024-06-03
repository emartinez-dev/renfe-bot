from calmjs.parse import es5
from calmjs.parse.unparsers.extractor import ast_to_dict

import os
import requests

URL_STATIONS = "https://www.renfe.com/content/dam/renfe/es/General/buscadores"\
               "/javascript/estacionesEstaticas.js"


class RenfeData:
    def __init__(self, origin: str, destination: str, departure_date: str,
                 return_date: str = ""):
        """
        format for date: dd/mm/yyyy
        date for back can be an empty string

        examples:
            origin: SEVILLA-SANTA JUSTA
            destination: CÓRDOBA

        this class depends on the station list at URL_STATIONS,
        if it doesn't exist it will be downloaded and parsed
        with calmjs. I didn't use CURL for portabily reasons
        """

        STATIONS_LIST = self.get_stations_list()
        self.origin = self.find_station(STATIONS_LIST, origin)
        self.destination = self.find_station(STATIONS_LIST, destination)
        if self.origin is None or self.destination is None:
            raise Exception(f"Origin or destination not found. Input: {origin} - {destination}")
        self.departure_date = departure_date
        self.return_date = return_date
        self.origin_code = self.origin[0]
        self.destination_code = self.destination[0]
        self.origin = self.origin[1]
        self.destination = self.destination[1]
        self.oneway = True if return_date == "" else False
        self.data = {
            "tipoBusqueda": "autocomplete",
            "currenLocation": "menuBusqueda",
            "vengoderenfecom": "SI",
            "cdgoOrigen": self.origin_code,
            "cdgoDestino": self.destination_code,
            "idiomaBusqueda": "ES",
            "FechaIdaSel": self.departure_date,
            "FechaVueltaSel": self.return_date,
            "desOrigen": self.origin,
            "desDestino": self.destination,
            "_fechaIdaVisual": self.departure_date,
            "_fechaVueltaVisual": self.return_date,
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

    def __repr__(self):
        return f"RenfeData({self.origin}, {self.destination}, {self.departure_date}, {self.return_date})"

    def get_post_data(self):
        return self.data

    def get_stations_list(self):
        filename = "estacionesEstaticas.js"
        if not os.path.exists(filename):
            print("Downloading stations list...")
            response = requests.get(URL_STATIONS)
            if response.status_code != 200:
                print(f"The resource at {URL_STATIONS} is not available")
                return None
            with open(filename, "w+") as f:
                f.write(response.text)
                print("Done!")
                f.close()

        with open(filename, "r") as f:
            file_content = f.read()
            stations = es5(file_content)
            stations_dict = ast_to_dict(stations)

        if "estacionesEstatico" in stations_dict:
            return stations_dict["estacionesEstatico"]
        return None

    def find_station(self, stations: list, station_name: str):
        for station in stations:
            if station["desgEstacionPlano"] == station_name:
                return (station["clave"], station["desgEstacionPlano"])
        return None
