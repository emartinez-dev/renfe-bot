import requests
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
RENFE_HOME = "https://www.renfe.com/es/es"
URL_STATIONS = "https://www.renfe.com/content/dam/renfe/es/General/buscadores"\
               "/javascript/estacionesEstaticas.js"
RENFE_SEARCH_URL = "https://venta.renfe.com/vol/buscarTren.do?Idioma=es&Pais=ES"

def get_stations_list():
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


BODY_TEST = "tipoBusqueda=autocomplete&currenLocation=menuBusqueda&vengoderenfecom=SI&cdgoOrigen=0071%2C50500%2C50500&cdgoDestino=0071%2C50504%2C50504&idiomaBusqueda=ES&FechaIdaSel=29%2F10%2F2023&FechaVueltaSel=30%2F10%2F2023&desOrigen=C%C3%93RDOBA&desDestino=POSADAS&_fechaIdaVisual=29%2F10%2F2023&_fechaVueltaVisual=30%2F10%2F2023&adultos_=1&ninos_=0&ninosMenores=0&numJoven=&numDorada=&codPromocional=&plazaH=false&Idioma=es&Pais=ES"
COOKIES_TEST = 'Search={"origen":{"code":"0071,50500,50500","name":"CÃ“RDOBA"},"destino":{"code":"0071,50504,50504","name":"POSADAS"},"pasajerosAdultos":1,"pasajerosNinos":0,"pasajerosSpChild":0}'


def find_station(stations: list, station_name: str):
    # check for similarities
    for station in stations:
        if station["desgEstacion"] == station_name:
            return (station["clave"], station["desgEstacion"])
    return None


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

        STATIONS_LIST = get_stations_list()
        origin = find_station(STATIONS_LIST, origin)
        destination = find_station(STATIONS_LIST, destination)
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
        return urlencode(self.data)

    def get_cookies_from_data(self):
        data = self.data
        origin_code = data["cdgoOrigen"]
        origin_name = data["desOrigen"]
        destination_code = data["cdgoDestino"]
        destination_name = data["desDestino"]
        return (f'{{"origen":{{"code":"{origin_code}","name":"{origin_name}"}},'
                f'"destino":{{"code":"{destination_code}","name":"{destination_name}"}},'
                '"pasajerosAdultos":1,"pasajerosNinos":0,"pasajerosSpChild":0}}')


def random_id():
    return "_" + random_string(4, "aA#")

def random_string(length, chars):
    mask = ""
    if "a" in chars:
        mask += string.ascii_lowercase
    if "A" in chars:
        mask += string.ascii_uppercase
    if "#" in chars:
        mask += string.digits
    if "!" in chars:
        mask += "~`!@#$%^&*()+-={}[]:\";'<>?,./|\\"
    result = ""
    for i in range(length):
        result += mask[random.randint(0, len(mask) - 1)]
    return result

def post_dwr_generateId(s, id):
    data = f"""
        callCount=1
        c0-scriptName=__System
        c0-methodName=generateId
        c0-id=0
        batchId=0
        instanceId=0
        page=%2Fvol%2Fsearch.do%3Fc%3D{id}
        scriptSessionId=
        windowName=
        """
    data = cleandoc(data)
    resp = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/__System.generateId.dwr", data=data)
    if (resp.status_code != 200):
        raise Exception("Error sending request")
    print(resp.text)
    pattern = r'r\.handleCallback\("0","0","(.*?)"\)'
    match = re.search(pattern, resp.text)

    if match:
        script_session_id = match.group(1)
        return script_session_id
    else:
        raise Exception("Error extracting ScriptSessionId")


def post_dwr_updateSessionObjects(s, id, script_session_id):
    data = f"""
        callCount=1
        windowName=
        c0-scriptName=buyManager
        c0-methodName=actualizaObjetosSesion
        c0-id=0
        c0-e1=string:{id}
        c0-e2=string:
        c0-param0=array:[reference:c0-e1,reference:c0-e2]
        batchId=1
        instanceId=0
        page=%2Fvol%2Fsearch.do%3Fc%3D{id}
        scriptSessionId={script_session_id}
    """
    data = cleandoc(data)
    resp = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/buyManager.actualizaObjetosSesion.dwr", data=data)
    if (resp.status_code != 200):
        raise Exception("Error sending request")
    print(resp.text)


def post_dwr_checkSession(s, id, script_session_id):
    data = f"""
        callCount=1
        windowName=
        c0-scriptName=sesionManager
        c0-methodName=checkSession
        c0-id=0
        batchId=2
        instanceId=0
        page=%2Fvol%2Fsearch.do%3Fc%3D{id}
        scriptSessionId={script_session_id}
    """
    data = cleandoc(data)
    resp = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/sesionManager.checkSession.dwr", data=data)
    if (resp.status_code != 200):
        raise Exception("Error sending request")
    print(resp.text)


def post_dwr_showModalCovid(s, id, date, script_session_id):
    data = f"""
        callCount=1
        windowName=
        c0-scriptName=trainManager
        c0-methodName=showModalCovid19
        c0-id=0
        c0-param0=string:{quote(date)}
        batchId=3
        instanceId=0
        page=%2Fvol%2Fsearch.do%3Fc%3D{id}
        scriptSessionId={script_session_id}
    """
    data = cleandoc(data)
    resp = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/trainManager.showModalCovid19.dwr", data=data)
    if (resp.status_code != 200):
        raise Exception("Error sending request")
    print(resp.text)


def post_dwr_obtenerUsuSession(s, id, script_session_id):
    data = f"""
        callCount=1
        windowName=
        c0-scriptName=loginManager
        c0-methodName=obtenerUsuSesion
        c0-id=0
        batchId=4
        instanceId=0
        page=%2Fvol%2Fsearch.do%3Fc%3D{id}
        scriptSessionId={script_session_id}
    """
    data = cleandoc(data)
    resp = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/loginManager.obtenerUsuSesion.dwr", data=data)
    if (resp.status_code != 200):
        raise Exception("Error sending request")
    print(resp.text)


def post_dwr_getTrainsList(s, id, date, script_session_id):
    data = f"""
        callCount=1
        windowName=
        c0-scriptName=trainManager
        c0-methodName=getTrainsList
        c0-id=0
        c0-param0=string:0
        c0-param1=string:{quote(date)}
        c0-e1=string:{id}
        c0-e2=string:{id}
        c0-param2=array:[reference:c0-e1,reference:c0-e2]
        batchId=5
        instanceId=0
        page=%2Fvol%2Fsearch.do%3Fc%3D{id}
        scriptSessionId={script_session_id}
    """
    data = cleandoc(data)
    print(time.time())
    resp = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/trainManager.getTrainsList.dwr", data=data, stream=True)
    if (resp.status_code != 200):
        raise Exception("Error sending request")
    print(resp.text)
    print(time.time())


def generate_page_id():
    timestamp = str(int(time.time() * 1000))
    random_part = str(int(random.random() * 1E16))
    page_id = f"{timestamp}-{random_part}"
    return page_id


with requests.Session() as s:
    # generate URL id
    id = random_id()
    # add headers and cookies
    s.headers.update(REQUEST_HEADERS)
    s.get(RENFE_HOME)
    # prepare data
    ride_data = RenfeData("02/11/2023", "03/11/2023", "POSADAS", "SEVILLA-SANTA JUSTA")
    # first request to find trains, we send a POST request with the formatted data and cookies
    s.cookies.set("Search", ride_data.get_cookies_from_data())
    resp = s.post(RENFE_SEARCH_URL, data=ride_data.get_post_data())
    if resp.status_code != 200:
        raise Exception("Error sending request")
    # update referer with the fake URL id, idk if it's really necessary to have always the same ID or it would just work normally without it
    s.headers.update({"Referer": f"https://venta.renfe.com/vol/search.do?c={id}"})
    dwr_page_id = generate_page_id()
    script_session_id = post_dwr_generateId(s, id)
    s.cookies.set("DWRSESSIONID", script_session_id)
    script_session_dwr = f"{script_session_id}/dwr-session-id"
    post_dwr_updateSessionObjects(s, id, script_session_dwr)
    post_dwr_checkSession(s, id, script_session_dwr)
    post_dwr_showModalCovid(s, id, ride_data.date_go, script_session_dwr)
    post_dwr_obtenerUsuSession(s, id, script_session_dwr)
    post_dwr_getTrainsList(s, id, ride_data.date_go, script_session_dwr)
    """
    print(resp.text)
    print(s.cookies)
    s.post("https://venta.renfe.com/vol/dwr/call/plaincall/buyManager.actualizaObjetosSesion.dwr")
    s.post("https://venta.renfe.com/vol/dwr/call/plaincall/sesionManager.checkSession.dwr")
    s.post("https://venta.renfe.com/vol/dwr/call/plaincall/loginManager.obtenerUsuSesion.dwr")
    final = s.post("https://venta.renfe.com/vol/dwr/call/plaincall/trainManager.getTrainsList.dwr", data="callCount=1\nwindowName=\nc0-scriptName=trainManager\nc0-methodName=getTrainsList\nc0-id=0\nc0-param0=string:0\nc0-param1=string:29%2F10%2F2023\nc0-e1=string:_byZp\nc0-e2=string:\nc0-param2=array:[reference:c0-e1,reference:c0-e2]\nbatchId=5\ninstanceId=0\npage=%2Fvol%2Fsearch.do%3Fc%3D_byZp\nscriptSessionId=9ndbI4KVU0JdYmNUV4nmzXXhXJo/MDXhXJo-KvybBBhMm\n")
    print(final.text)
    """

