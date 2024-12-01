import configparser
from datetime import datetime, time
from textwrap import dedent
from typing import Dict, Any, List

import requests
import telebot

from errors import StationNotFound
from messages import user_messages
from models import StationRecord, TrainRideFilter, TrainRideRecord
from scraper import Scraper
from storage import StationsStorage


def init_bot() -> None:
    """Assist the user to initialize the configuration of the bot."""
    config = configparser.ConfigParser()
    config.read("config.ini")

    if "Telegram" not in config:
        print(
            dedent("""\
        Hola! Voy a ayudarte a configurar tu propio RenfeBot para que te avise
        cuando haya billetes disponibles para el trayecto que quieras.

        Antes de nada y por motivos obvios, necesitas tener una cuenta de Telegram antes
        de crear un bot de Telegram.

        Para crear el bot, debes ir a este enlace y empezar una conversación con el
        asistente -> https://t.me/botfather
        Una vez empieces la conversación, el asistente te irá guiando durante todo el
        proceso, solo tienes que escribir /newbot para crear uno

        Después de introducir el nombre y su nombre de usuario, el asistente te dará
        tanto el token de acceso a la API como el nombre de usuario del bot. Guarda la URL
        para poder interactuar con él e introduce el token a continuación.

        Puede que al correr el script en Docker, no te deje introducir el token, puedes saltarte
        este paso y escribirlo directamente en el archivo config.ini con este formato:
        ---
            [Telegram]
            secret_token=123456789:ABCdefGhIjKlmNopQrsTuvWxYz
        ---
        """)
        )
        config["Telegram"] = {}

    if "secret_token" not in config["Telegram"]:
        while "secret_token" not in config["Telegram"]:
            token = input("Introduce el token de tu bot: ")
            url = f"https://api.telegram.org/bot{token}/getMe"

            r = requests.get(url)

            if r.status_code == 200:
                print("Bot creado correctamente!")
                config["Telegram"]["secret_token"] = token
            elif r.status_code == 401:
                print("Token incorrecto, vuelve a intentarlo")
            else:
                print("Ha ocurrido un error, vuelve a intentarlo")

    with open("config.ini", "w") as configfile:
        config.write(configfile)


def get_bot_token() -> str:
    """Read the configuration file to obtain the bot's secret token. If it's not there, the user
    is prompted to configure it properly.

    :return: The bot instance secret token
    :rtype: str
    """
    config = configparser.ConfigParser()
    config.read("config.ini")

    if "Telegram" not in config or "secret_token" not in config["Telegram"]:
        init_bot()
        config.read("config.ini")

    return config["Telegram"]["secret_token"]


TOKEN = get_bot_token()
bot = telebot.TeleBot(TOKEN)
searching = False
print("Ya estoy corriendo! Corre a Telegram e interactúa conmigo")


@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message):
    assert message.from_user is not None
    bot.send_message(
        message.chat.id,
        dedent(
            f"Hola {message.from_user.first_name}. "
            "Bienvenido a tu bot de Renfe. Te ayudaré a encontrar "
            "billetes de tren para tus viajes. Para empezar, escribe "
            "/ayuda para ver los comandos disponibles."
        ),
    )


@bot.message_handler(commands=["ayuda"])
def send_help(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        dedent("""\
        /ayuda - Muestra los comandos disponibles
        /buscar - Busca billetes de tren
        /cancelar - Cancela la búsqueda en curso
        """),
    )


"""
@bot.message_handler(commands=["reintentar"])
def send_retry(message: telebot.types.Message):
    if searching:
        bot.send_message(
            message.chat.id,
            "Ya hay una búsqueda en curso, por favor espera o utiliza /cancelar para cancelarla",
        )
        return
    try:
        with open("last_input.json", "r", encoding="utf-8") as f:
            context = json.load(f)
        search_trains(message, context)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "No hay ninguna búsqueda anterior")


@bot.message_handler(commands=["debug"])
def send_debug(message: telebot.types.Message):
    assert message.from_user is not None
    assert message.from_user.username is not None

    logs = os.listdir("logs")
    user_logs = []
    for log in logs:
        if message.from_user.username in log:
            user_logs.append(log)

    if len(user_logs) == 0:
        bot.send_message(message.chat.id, "No hay logs disponibles")
    else:
        bot.send_message(
            message.chat.id, "Envía este documento a los desarrolladores para que puedan ayudarte:"
        )
        user_logs.sort(reverse=True)
        with open(f"logs/{user_logs[0]}", "rb", encoding="utf-8") as f:
            bot.send_document(message.chat.id, f.read())
"""


@bot.message_handler(commands=["cancelar"])
def send_cancel(message: telebot.types.Message):
    global searching
    if searching:
        bot.send_message(message.chat.id, "La búsqueda en curso ha sido cancelada")
        searching = False
    else:
        bot.send_message(message.chat.id, "No hay ninguna búsqueda en curso")


@bot.message_handler(commands=["buscar"])
def start_user_search(message: telebot.types.Message):
    assert message.from_user is not None
    if searching:
        bot.send_message(
            message.chat.id,
            "Ya hay una búsqueda en curso, por favor espera o utiliza /cancelar para cancelarla",
        )
        return
    context = {"user_id": message.from_user.id}
    bot.send_message(message.chat.id, "🚉 ¿Desde qué estación sales?")
    bot.register_next_step_handler(message, ask_for_origin, context)


def ask_for_origin(message: telebot.types.Message, context):
    try:
        if message.text is None:
            raise StationNotFound
        station = StationsStorage.get_station(message.text.upper())
        context["origin"] = station
        bot.send_message(message.chat.id, "🚉 ¿A qué estación vas?")
        bot.register_next_step_handler(message, ask_for_destination, context)

    except StationNotFound:
        bot.send_message(message.chat.id, user_messages["station_not_found"])
        bot.register_next_step_handler(message, ask_for_origin, context)


def ask_for_destination(message: telebot.types.Message, context):
    try:
        if message.text is None:
            raise StationNotFound
        station = StationsStorage.get_station(message.text.upper())
        context["destination"] = station
        bot.send_message(message.chat.id, "📅 ¿Cuándo sales? (dd/mm/aaaa)")
        bot.register_next_step_handler(message, ask_for_departure_date, context)

    except StationNotFound:
        bot.send_message(message.chat.id, user_messages["station_not_found"])
        bot.register_next_step_handler(message, ask_for_destination, context)


def ask_for_departure_date(message: telebot.types.Message, context):
    assert message.text is not None
    date = [int(x) for x in message.text.split("/")]
    if len(date) == 3:
        day, month, year = date
        try:
            context["departure_date"] = datetime(year, month, day)
            bot.send_message(message.chat.id, "🔙 ¿Necesitas billete de vuelta? (S/N)")
            bot.register_next_step_handler(message, ask_for_return, context)
        except ValueError:
            bot.send_message(message.chat.id, user_messages["wrong_date"])
            bot.register_next_step_handler(message, ask_for_departure_date, context)
    else:
        bot.send_message(message.chat.id, user_messages["wrong_date"])
        bot.register_next_step_handler(message, ask_for_departure_date, context)


def ask_for_return(message: telebot.types.Message, context):
    assert message.text is not None
    if message.text.lower() in ["si", "s", "y", "yes"]:
        bot.send_message(message.chat.id, "📅 ¿Cuándo vuelves? (dd/mm/aaaa)")
        bot.register_next_step_handler(message, ask_for_return_date, context)
    else:
        context["return_date"] = None
        bot.send_message(
            message.chat.id, "¿Quieres filtrar los resultados (hora, precio...)? (S/N)"
        )
        bot.register_next_step_handler(message, ask_for_filter, context)


def ask_for_return_date(message: telebot.types.Message, context):
    assert message.text is not None
    date = [int(x) for x in message.text.split("/")]
    if len(date) == 3:
        day, month, year = date
        try:
            context["return_date"] = datetime(year, month, day)
            bot.send_message(
                message.chat.id, "¿Quieres filtrar los resultados (hora, precio...)? (S/N)"
            )
            bot.register_next_step_handler(message, ask_for_filter, context)
        except ValueError:
            bot.send_message(message.chat.id, user_messages["wrong_date"])
            bot.register_next_step_handler(message, ask_for_return_date, context)
    else:
        bot.send_message(message.chat.id, user_messages["wrong_date"])
        bot.register_next_step_handler(message, ask_for_return_date, context)


def ask_for_filter(message: telebot.types.Message, context):
    assert message.text is not None
    if message.text.lower() in ["si", "s", "y", "yes"]:
        bot.send_message(
            message.chat.id, "💵 ¿Precio máximo? (introduce 0 si no quieres filtrar por precio)"
        )
        bot.register_next_step_handler(message, ask_for_max_price, context)
    else:
        search_trains(message, context)


def ask_for_max_price(message: telebot.types.Message, context):
    assert message.text is not None
    max_price = int(message.text)
    context["max_price"] = None if max_price == 0 else max_price
    bot.send_message(
        message.chat.id,
        "⏳ ¿Duración máxima del trayecto? (en minutos)",
    )
    bot.register_next_step_handler(message, get_max_duration, context)


def get_max_duration(message: telebot.types.Message, context):
    assert message.text is not None
    context["max_duration_minutes"] = int(message.text)
    bot.send_message(message.chat.id, "🕒 ¿A partir de qué hora quieres salir? (hh:mm)")
    bot.register_next_step_handler(message, ask_for_min_departure_hour, context)


def ask_for_min_departure_hour(message: telebot.types.Message, context):
    assert message.text is not None
    h, m = message.text.split(":")
    context["min_departure_hour"] = time(int(h), int(m))
    bot.send_message(message.chat.id, "🕒 ¿Y como muy tarde? (hh:mm)")
    bot.register_next_step_handler(message, ask_for_max_departure_hour, context)


def ask_for_max_departure_hour(message: telebot.types.Message, context):
    assert message.text is not None
    h, m = message.text.split(":")
    context["max_departure_hour"] = time(int(h), int(m))
    if context.get("return_date", None) is None:
        search_trains(message, context)
    else:
        bot.send_message(message.chat.id, "🕒 ¿A partir de qué hora quieres volver? (hh:mm)")
        bot.register_next_step_handler(message, ask_for_min_return_hour, context)


def ask_for_min_return_hour(message: telebot.types.Message, context):
    assert message.text is not None
    h, m = message.text.split(":")
    context["min_return_hour"] = time(int(h), int(m))
    bot.send_message(message.chat.id, "🕒 ¿Y como muy tarde? (hh:mm)")
    bot.register_next_step_handler(message, ask_for_max_return_hour, context)


def ask_for_max_return_hour(message: telebot.types.Message, context):
    assert message.text is not None
    h, m = message.text.split(":")
    context["max_return_hour"] = time(int(h), int(m))
    search_trains(message, context)


def get_tickets_message(
    trains: List[TrainRideRecord], origin: StationRecord, destination: StationRecord
):
    message = (
        f"He encontrado varios billetes de {origin.name.capitalize()} a "
        f"{destination.name.capitalize()}:\n\n"
    )
    for train in trains:
        message += str(train)
    return message


def search_trains(message: telebot.types.Message, context: Dict[str, Any]):
    global searching
    searching = True
    bot.send_message(message.chat.id, "🔎 Buscando billetes...")
    departure_done = False
    return_done = context.get("return_date", None) is None

    scraper = Scraper(
        context["origin"],
        context["destination"],
        context["departure_date"],
        context.get("return_date"),
    )
    departure_filter = TrainRideFilter(
        origin=context["origin"].name,
        destination=context["destination"].name,
        departure_date=context["departure_date"],
        min_departure_hour=context.get("min_departure_hour"),
        max_departure_hour=context.get("max_departure_hour"),
        max_duration_minutes=context.get("max_duration_minutes"),
        max_price=context.get("max_price"),
    )

    if not return_done:
        return_filter = TrainRideFilter(
            origin=context["destination"].name,
            destination=context["origin"].name,
            departure_date=context.get("return_date"),
            min_departure_hour=context.get("min_return_hour"),
            max_departure_hour=context.get("max_return_hour"),
            max_duration_minutes=context.get("max_duration_minutes"),
            max_price=context.get("max_price"),
        )

    try:
        while not departure_done or not return_done:
            trains = scraper.get_trainrides()
            if not departure_done:
                departure_trains = departure_filter.filter_rides(trains)
                departure_done = len(departure_trains) > 0
                if departure_done:
                    bot.send_message(
                        message.chat.id,
                        get_tickets_message(
                            departure_trains, context["origin"], context["destination"]
                        ),
                    )
            if not return_done:
                return_trains = return_filter.filter_rides(trains)
                return_done = len(return_trains) > 0
                if return_done:
                    bot.send_message(
                        message.chat.id,
                        get_tickets_message(
                            return_trains, context["destination"], context["origin"]
                        ),
                    )
        searching = False
        print("Búsqueda completada")

    except Exception as e:
        bot.send_message(message.chat.id, "Algo ha fallado, info:")
        bot.send_message(message.chat.id, e.__str__())
        print("La búsqueda ha fallado")
        searching = False


bot.polling()
