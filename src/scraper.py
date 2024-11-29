from datetime import datetime
import json
import random
import re
from typing import Any, Dict, Generator, Optional
import string
import urllib.parse

import requests

from errors import InvalidDWRToken
from models import StationRecord
from storage import StationsStorage

SEARCH_URL = "https://venta.renfe.com/vol/buscarTren.do?Idioma=es&Pais=ES"

DWR_ENDPOINT = "https://venta.renfe.com/vol/dwr/call/plaincall/"
SYSTEM_ID_URL = f"{DWR_ENDPOINT}__System.generateId.dwr"
UPDATE_SESSION_URL = f"{DWR_ENDPOINT}buyEnlacesManager.actualizaObjetosSesion.dwr"
TRAIN_LIST_URL = f"{DWR_ENDPOINT}trainEnlacesManager.getTrainsList.dwr"


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
        self.batch_id = get_idx()

        self.dwr_token = None
        self.script_session_id = None

    def do_search(self) -> None:
        """Encapsulate the API calls that must be done to input the Renfe search page"""
        data = self._create_search_payload()
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

    def do_get_dwr_token(self) -> None:
        """Encapsulate the API calls that must be done to obtain the DWR token"""
        payload = self._create_generate_id_payload()
        self.api.post(SYSTEM_ID_URL, data=payload)

        payload = self._create_generate_id_payload()
        r = self.api.post(SYSTEM_ID_URL, data=payload)
        assert r.ok

        self.dwr_token = extract_dwr_token(r.text)
        self.api.cookies.set("DWRSESSIONID", self.dwr_token, path="/vol", domain="venta.renfe.com")
        self.script_session_id = create_session_script_id(self.dwr_token)

    def do_update_session_objects(self) -> None:
        """Encapsulate the API calls that must be done to update the DWR session objects"""
        payload = self._create_update_session_objects_payload()
        r = self.api.post(UPDATE_SESSION_URL, data=payload)
        assert r.ok

    def do_get_train_list(self) -> Dict[str, Any]:
        """Encapsulate the API calls that must be done to get and parse the trains list"""
        payload = self._create_get_train_list_payload()
        r = self.api.post(TRAIN_LIST_URL, data=payload)
        assert r.ok
        return extract_train_list(r.text)

    def _create_search_payload(self) -> Dict[str, str]:
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
        return_date = "" if self.return_date is None else self.return_date.strftime(date_format)
        payload = {
            "tipoBusqueda": "autocomplete",
            "currenLocation": "menuBusqueda",
            "vengoderenfecom": "SI",
            "desOrigen": self.origin.name,
            "desDestino": self.destination.name,
            "cdgoOrigen": self.origin.code,
            "cdgoDestino": self.destination.code,
            "idiomaBusqueda": "ES",
            "FechaIdaSel": self.departure_date.strftime(date_format),
            "FechaVueltaSel": return_date,
            "_fechaIdaVisual": self.departure_date.strftime(date_format),
            "_fechaVueltaVisual": return_date,
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

    def _create_generate_id_payload(self) -> str:
        """Generates the payload for the API calls to the generateId DWR endpoint

        :param batch_id: batchId of the operation
        :type batch_id: int
        :param search_id: defaults to None
        :type search_id: Optional[str], optional
        :return: Payload that can be POST to the generateId DWR endpoint
        :rtype: str
        """
        if self.search_id is None:
            page = "page=%2Fvol%2FbuscarTrenEnlaces.do\n"
        else:
            page = f"page=%2Fvol%2FbuscarTrenEnlaces.do%3Fc%3D{self.search_id}\n"

        payload = (
            "callCount=1\n"
            "c0-scriptName=__System\n"
            "c0-methodName=generateId\n"
            "c0-id=0\n"
            f"batchId={str(next(self.batch_id))}\n"
            "instanceId=0\n"
            f"{page}"
            "scriptSessionId=\n"
            "windowName=\n"
        )
        return payload

    def _create_update_session_objects_payload(self) -> str:
        """Generates the payload for the API calls to the update session objects DWR endpoint

        :return: Payload that can be POST to the actualizaObjetosSesion DWR endpoint
        :rtype: str
        """
        payload = (
            "callCount=1\n"
            "windowName=\n"
            "c0-scriptName=buyEnlacesManager\n"
            "c0-methodName=actualizaObjetosSesion\n"
            "c0-id=0\n"
            f"c0-e1=string:{self.search_id}\n"
            "c0-e2=string:\n"
            "c0-param0=array:[reference:c0-e1,reference:c0-e2]\n"
            f"batchId={str(next(self.batch_id))}\n"
            "instanceId=0\n"
            f"page=%2Fvol%2FbuscarTrenEnlaces.do%3Fc%3D{self.search_id}\n"
            f"scriptSessionId={self.script_session_id}\n"
        )
        return payload

    def _create_get_train_list_payload(self) -> str:
        date_format = "%d/%m/%Y"
        departure_date = (
            "" if self.departure_date is None else self.departure_date.strftime(date_format)
        )
        return_date = "" if self.return_date is None else self.return_date.strftime(date_format)
        payload = (
            "callCount=1\n"
            "windowName=\n"
            "c0-scriptName=trainEnlacesManager\n"
            "c0-methodName=getTrainsList\n"
            "c0-id=0\n"
            "c0-e1=string:false\n"
            "c0-e2=string:false\n"
            "c0-e3=string:false\n"
            "c0-e4=string:\n"
            "c0-e5=string:\n"
            "c0-e6=string:\n"
            "c0-e7=string:\n"
            f"c0-e8=string:{urllib.parse.quote_plus(departure_date)}\n"
            f"c0-e9=string:{urllib.parse.quote_plus(return_date)}\n"
            "c0-e10=string:1\n"
            "c0-e11=string:0\n"
            "c0-e12=string:0\n"
            f"c0-e13=string:{"I" if self.return_date is None else "IV"}\n"
            "c0-e14=string:\n"
            "c0-param0=Object_Object:{atendo:reference:c0-e1, sinEnlace:reference:c0-e2, "
            "plazaH:reference:c0-e3, tipoFranjaI:reference:c0-e4, tipoFranjaV:reference:c0-e5, "
            "horaFranjaIda:reference:c0-e6, horaFranjaVuelta:reference:c0-e7, fechaSalida:reference"
            ":c0-e8, fechaVuelta:reference:c0-e9, adultos:reference:c0-e10, ninos:reference:c0-e11,"
            " ninosMenores:reference:c0-e12, trayecto:reference:c0-e13, idaVuelta:reference:c0-e14}"
            "\n"
            f"batchId={next(self.batch_id)}\n"
            "instanceId=0\n"
            f"page=%2Fvol%2FbuscarTrenEnlaces.do%3Fc%3D{self.search_id}\n"
            f"scriptSessionId={self.script_session_id}\n"
        )
        return payload


def get_idx() -> Generator:
    """Yields numbers from 0 to inf

    :yield: num
    :rtype: int
    """
    num = 0
    while True:
        yield num
        num += 1


def extract_dwr_token(response_text: str) -> str:
    """Extracts the DWR token from the API response of the generateId calls

    :param response_text: The body of the generateId POST response
    :type response_text: str
    :raises InvalidDWRToken: If the token is not found in the response body
    :return: The DWR token itself
    :rtype: str
    """
    pattern = r'r\.handleCallback\("[^"]+","[^"]+","([^"]+)"\)'
    match = re.search(pattern, response_text)

    if match:
        return match.group(1)
    else:
        raise InvalidDWRToken


def extract_train_list(response_text: str) -> Dict[str, Any]:
    """Extracts the train list returned as JS code by the DWR call

    :param response_text: The response from the trains API call
    :type response_text: str
    :return: Trains JSON
    :rtype: Dict[str, Any]
    """
    match = re.search(r'r\.handleCallback\([^,]+,\s*[^,]+,\s*(\{.*\})\);', response_text, re.DOTALL)
    assert match is not None
    js_object = match.group(1)
    js_object = js_object.strip()  # Remove any leading/trailing whitespace
    js_object = js_object.replace("Vuelta:", "Vuelta") # Remove semicolon inside value
    js_object = js_object.replace("://", "//") # Remove semicolon inside value
    js_object = re.sub(r',\s*}', '}', js_object)  # Remove trailing commas before closing braces
    js_object = re.sub(r',\s*]', ']', js_object)  # Remove trailing commas before closing brackets
    js_object = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', js_object)  # Quote keys
    js_object = js_object.replace("'", '"')  # Replace single quotes with double quotes
    parsed_data = json.loads(js_object)
    return parsed_data


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
    """Generate the query parameter for Renfe searches, which has the format '_Aa#'

    :return: search_id
    :rtype: str
    """
    search_id = "_"
    for _ in range(4):
        search_id += random.choice(string.ascii_letters + string.digits)
    return search_id


def create_session_script_id(dwr_token: str) -> str:
    """Creates the sessionScriptId parameter required for the trains DWR calls, combining the DWR
    token with a token based on the timestamp and another one random

    :param dwr_token: The DWR token itself
    :type dwr_token: str
    :return: The session script id
    :rtype: str
    """
    date_token = tokenify(int(datetime.now().timestamp() * 1000))
    random_token = tokenify(int(random.random() * 1e16))
    return f"{dwr_token}/{date_token}-{random_token}"


def tokenify(number: int):
    """Tokenify function used by the DWR framework, rewritten from Java to Python

    :param number: _description_
    :type number: int
    :return: _description_
    :rtype: _type_
    """
    tokenbuf = []
    charmap = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ*$"
    remainder = number

    while remainder > 0:
        tokenbuf.append(charmap[remainder & 0x3F])
        remainder //= 64

    return "".join(tokenbuf)


