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


def load_last_search_results():
    try:
        with open('last_search_results.json', 'r') as f:
            last_results = json.load(f)
            f.close()
        return last_results
    except FileNotFoundError:
        return None


def compare_search_results(last_results, current_results):
    if last_results is None or current_results is None:
        return False
    if len(last_results) != len(current_results):
        return False
    for last, current in zip(last_results, current_results):
        if last != current:
            return False
    return True
