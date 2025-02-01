"""This module contains the main logic of the bot. The search process is a finite state machine."""

import asyncio
from datetime import datetime

from pydantic import BaseModel
from telebot import async_telebot, asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states import State, StatesGroup
from telebot.states.asyncio.context import StateContext
from telebot.states.asyncio.middleware import StateMiddleware
from telebot.types import Message

from config import get_bot_token
from messages import user_messages as msg
from models import StationRecord
from validators import validate_station, validate_date, validate_float


class SearchStates(StatesGroup):
    """SearchStates is a class that defines the different states for the search process."""
    origin = State()
    destination = State()
    departure_date = State()
    needs_return = State()
    return_date = State()
    needs_filter = State()
    max_price = State()
    max_duration_minutes = State()
    searching = State()


class SearchContext(BaseModel):
    """SearchContext is a class that holds the context of the search process."""
    user_id: int
    origin: StationRecord | None = None
    destination: StationRecord | None = None
    departure_date: datetime | None = None
    return_date: datetime | None = None
    max_price: float | None = None
    max_duration_minutes: float | None = None


TOKEN = get_bot_token()
bot = telebot.TeleBot(TOKEN)
searching = False
print("Ya estoy corriendo! Corre a Telegram e interactúa conmigo con los comandos /start o /help")


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
        /reintentar - Vuelve a lanzar la última búsqueda
        /cancelar - Cancela la búsqueda en curso
        """),
    )


@bot.message_handler(commands=["reintentar"])
def send_retry(message: telebot.types.Message):
    if searching:
        bot.send_message(
            message.chat.id,
            "Ya hay una búsqueda en curso, por favor espera o utiliza /cancelar para cancelarla",
        )
        return
    try:
        with open("last_input.pkl", "rb") as f:
            context = pickle.load(f)
        search_trains(message, context)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "No hay ninguna búsqueda anterior")


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
        if message.text is not None:
            possible_stations = StationsStorage.find_station(message.text)
            if len(possible_stations) == 0:
                bot.send_message(message.chat.id, user_messages["station_not_found"])
            else:
                bot.send_message(
                    message.chat.id,
                    (
                        f"No he encontrado la estación {message.text} pero he encontrado estas: \n"
                        f"{'\n'.join(possible_stations)}."
                        "\nPor favor, introduce la tuya de nuevo"
                    ),
                )
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
        if message.text is not None:
            possible_stations = StationsStorage.find_station(message.text)
            if len(possible_stations) == 0:
                bot.send_message(message.chat.id, user_messages["station_not_found"])
            else:
                bot.send_message(
                    message.chat.id,
                    (
                        f"No he encontrado la estación {message.text} pero he encontrado estas: \n"
                        f"{'\n'.join(possible_stations)}."
                        "\nPor favor, introduce la tuya de nuevo"
                    ),
                )
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

    try:
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

        with open("last_input.pkl", "wb") as f:
            pickle.dump(context, f)

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
            if not return_done or not departure_done:
                time_module.sleep(60)
        searching = False
        print("Búsqueda completada")

    except InvalidTrainRideFilter:
        searching = False
        bot.send_message(
            message.chat.id,
            (
                "El filtro introducido no es válido o no se encontró ningún tren con estos parámetros,"
                " por favor, inténtalo de nuevo."
            ),
        )

    except InvalidDWRToken:
        searching = False
        bot.send_message(
            message.chat.id,
            (
                "Si esto ocurre, Renfe ha actualizado por fin su web. Por favor, abre una issue en "
                "github para que pueda revisarlo."
            ),
        )

    except BaseException as e:
        searching = False
        bot.send_message(
            message.chat.id, f"Oops, algo se ha roto y no sé el qué. Aquí va toda la traza: {e}"
        )


bot.polling()
