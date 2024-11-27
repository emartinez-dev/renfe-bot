from datetime import datetime
import random
import requests
import string
from typing import Any, Dict, Optional

from models import StationRecord
from storage import StationsStorage

SEARCH_URL = "https://venta.renfe.com/vol/buscarTren.do?Idioma=es&Pais=ES"


def create_payload(
    origin: StationRecord,
    destination: StationRecord,
    departure_date: datetime,
    return_date: Optional[datetime] = None,
) -> Dict[str, str]:
    """Creates the payload that will be send by POST to the Renfe search URL

    :param origin: Origin station
    :type origin: StationRecord
    :param destination: Destination station
    :type destination: StationRecord
    :param departure_date: The departure date
    :type departure_date: datetime
    :param return_date: The return date, defaults to None as it's not required
    :type return_date: Optional[datetime], optional
    :return: The payload dict
    :rtype: Dict[str, str]
    """
    date_format = "%d/%m/%Y"
    payload = {
        "tipoBusqueda": "autocomplete",
        "currenLocation": "menuBusqueda",
        "vengoderenfecom": "SI",
        "desOrigen": origin.name,
        "desDestino": destination.name,
        "cdgoOrigen": origin.code,
        "cdgoDestino": destination.code,
        "idiomaBusqueda": "ES",
        "FechaIdaSel": departure_date.strftime(date_format),
        "FechaVueltaSel": "" if return_date is None else return_date.strftime(date_format),
        "_fechaIdaVisual": departure_date.strftime(date_format),
        "_fechaVueltaVisual": "" if return_date is None else return_date.strftime(date_format),
        "adultos_": "1",
        "ninos_": "0",
        "ninosMenores": "0",
        "codPromocional": "",
        "plazaH": "false",
        "sinEnlace": "false",
        "asistencia": "false",
        "franjaHoraI": "",
        "franjaHoraV": "",
        "Idioma": "es",
        "Pais": "ES",
    }
    return payload


def create_cookiedict(
    origin: StationRecord,
    destination: StationRecord,
) -> Dict[str, Any]:
    """Creates the cookie for the train search

    :param origin: Origin station
    :type origin: StationRecord
    :param destination: Destination station
    :type destination: StationRecord
    :return: The cookie dictionary
    :rtype: Dict[str, Any]
    """
    search = {
        "origen": {"code": origin.code, "name": origin.name},
        "destino": {"code": destination.code, "name": destination.name},
        "pasajerosAdultos": 1,
        "pasajerosNinos": 0,
        "pasajerosSpChild": 0,
    }
    cookie = {"name": "Search", "value": str(search), "domain": ".renfe.com", "path": "/"}
    return cookie


def create_search_id() -> str:
    search_id = "_"
    for _ in range(4):
        search_id += random.choice(string.ascii_letters + string.digits)
    return search_id


class Scraper:
    def __init__(
        self,
        origin: StationRecord,
        destination: StationRecord,
        departure_date: datetime,
        return_date: Optional[datetime] = None,
    ):
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date
        self.return_date = return_date

        self.api = requests.Session()
        self.search_id = create_search_id()

    def create_search(self):
        data = create_payload(self.origin, self.destination, self.departure_date, self.return_date)
        cookies = create_cookiedict(self.origin, self.destination)
        self.api.cookies.set(**cookies)
        self.api.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        r = self.api.post(SEARCH_URL, data=data, allow_redirects=True)
        assert r.ok
