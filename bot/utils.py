import json
from textwrap import dedent


def export_input(user_params):
    with open('last_input.json', 'w+') as f:
        json.dump(user_params, f, indent=4)
        f.close()


def message_header(way, number, origin: str, destination):
    if way == "vuelta":
        origin, destination = destination, origin
    billetes = "billetes"
    if number == 1:
        billetes = "billete"
    return dedent(f"""He encontrado {number} {billetes} de {origin.title()} a {destination.title()} con los parámetros introducidos:\n\n""")


def get_tickets_message(trains: tuple, origin, destination):
    message = ""
    for way in trains:
        if len(way) > 0:
            message += message_header(way[0]['direction'], len(way), origin, destination)
            for train in way:
                message += f"🚆 Tren {train['train_type']} - 🕒 {train['departure']} - {train['arrival']} 🕙 - {train['price']} €\n"
            message += "\n"
    return message
