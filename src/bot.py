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
state_storage = StateMemoryStorage()  # TODO: Don't use this in production, (idk why, but use redis)
bot = async_telebot.AsyncTeleBot(TOKEN, state_storage=state_storage)
print("Ya estoy corriendo! Corre a Telegram e interactúa conmigo con los comandos /start o /help")


@bot.message_handler(commands=["start"])
async def send_welcome(message: Message):
    """Sends a welcome message to the user who initiated the conversation."""
    assert message.from_user is not None
    username = message.from_user.first_name
    await bot.send_message(message.chat.id, msg["welcome"].format(username))


@bot.message_handler(commands=["ayuda"])
async def send_help(message: Message):
    """Sends a help message to the user who requested it."""
    await bot.send_message(message.chat.id, msg["help"])

'''
@bot.message_handler(commands=["reintentar"])
def send_retry(message: Message):
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
def send_cancel(message: Message):
    global searching
    if searching:
        bot.send_message(message.chat.id, "La búsqueda en curso ha sido cancelada")
        searching = False
    else:
        bot.send_message(message.chat.id, "No hay ninguna búsqueda en curso")
'''

@bot.message_handler(commands=["buscar"])
async def start_search(message: Message, state: StateContext):
    """Starts the search process by asking the user for the origin station."""
    assert message.from_user is not None
    await state.set(SearchStates.origin)
    await state.add_data(user_id=message.from_user.id)
    await bot.send_message(message.chat.id, msg["start"])


@bot.message_handler(state=SearchStates.origin)
async def origin_get(message: Message, state: StateContext):
    """Gets the origin station from the user and asks for the destination station."""
    origin = validate_station(message)

    if not origin:
        await bot.send_message(message.chat.id, origin.error_message)
    else:
        await state.set(SearchStates.destination)
        await state.add_data(origin=origin.station)
        await bot.send_message(message.chat.id, msg["destination"])


@bot.message_handler(state=SearchStates.destination)
async def destination_get(message: Message, state: StateContext):
    """Gets the destination station from the user and asks for the departure date."""
    destination = validate_station(message)

    if not destination:
        await bot.send_message(message.chat.id, destination.error_message)
    else:
        await state.set(SearchStates.departure_date)
        await state.add_data(destination=destination.station)
        await bot.send_message(message.chat.id, msg["destination_date"])


@bot.message_handler(state=SearchStates.departure_date)
async def departure_date_get(message: Message, state: StateContext):
    """Gets the departure date from the user and asks if they need a return ticket."""
    departure_datetime = validate_date(message)

    if not departure_datetime:
        await bot.send_message(message.chat.id, departure_datetime.error_message)
    else:
        await state.set(SearchStates.needs_return)
        await state.add_data(departure_datetime=departure_datetime.date)
        await bot.send_message(message.chat.id, msg["needs_return"])


@bot.message_handler(state=SearchStates.needs_return)
async def return_get(message: Message, state: StateContext):
    """Gets the user's choice about needing a return ticket and asks for the date if he needs."""
    if message.text is not None and message.text.lower() in ["si", "s", "y", "yes"]:
        await state.set(SearchStates.departure_date)
        await bot.send_message(message.chat.id, msg["return_date"])
    else:
        await state.set(SearchStates.needs_filter)
        await bot.send_message(message.chat.id, msg["needs_filter"])


@bot.message_handler(state=SearchStates.return_date)
async def return_date_get(message: Message, state: StateContext):
    """Gets the return date from the user and asks if they want to filter the results."""
    return_datetime = validate_date(message)

    if not return_datetime:
        await bot.send_message(message.chat.id, return_datetime.error_message)
    else:
        await state.set(SearchStates.needs_filter)
        await state.add_data(return_datetime=return_datetime.date)
        await bot.send_message(message.chat.id, msg["needs_filter"])


@bot.message_handler(state=SearchStates.needs_filter)
async def ask_for_filter(message: Message, state: StateContext):
    """Asks the user if they want to filter the results and starts the search process if not."""
    if message.text is not None and message.text.lower() in ["si", "s", "y", "yes"]:
        await state.set(SearchStates.max_price)
        await bot.send_message(message.chat.id, msg["max_price"])
    else:
        await state.set(SearchStates.searching)
        await bot.send_message(message.chat.id, msg["searching"])
        async with state.data() as data: # type: ignore
            await bot.send_message(message.chat.id, data)


@bot.message_handler(state=SearchStates.max_price)
async def ask_for_max_price(message: Message, state: StateContext):
    """Asks the user for the maximum price and starts the search process."""
    parsed = validate_float(message)

    if not parsed:
        await bot.send_message(message.chat.id, parsed.error_message)
    else:
        await state.set(SearchStates.max_duration_minutes)
        await state.add_data(max_price=None if parsed.number == 0 else parsed.number)
        await bot.send_message(message.chat.id, msg["max_duration"])


@bot.message_handler(state=SearchStates.max_duration_minutes)
async def get_max_duration(message: Message, state: StateContext):
    """Gets the maximum duration of the trip and starts the search process."""
    parsed = validate_float(message)

    if not parsed:
        await bot.send_message(message.chat.id, parsed.error_message)
    else:
        await state.set(SearchStates.searching)
        await state.add_data(max_duration=None if parsed.number == 0 else parsed.number)
        await bot.send_message(message.chat.id, msg["searching"])
        st = await state.get()
        await bot.send_message(message.chat.id, st)


'''
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


def search_trains(message: Message, context: Dict[str, Any]):
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
'''

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.setup_middleware(StateMiddleware(bot))

asyncio.run(bot.infinity_polling())
