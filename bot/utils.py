import Levenshtein
import json
import pandas as pd
from textwrap import dedent


def sanitize_station_input(user_input: str):
    with open('resources/stations.txt', 'r') as f:
        stations = [line.strip() for line in f]

    sanitized_input = user_input.upper().strip()
    closest_station = None
    closest_distance = 100

    for station in stations:
        distance = Levenshtein.distance(sanitized_input, station)
        if distance < closest_distance:
            closest_station = station
            closest_distance = distance

    if closest_distance > 2:
        return None
    return closest_station


def export_input(user_params):
    with open('resources/last_input.json', 'w') as f:
        json.dump(user_params, f, indent=4)
        f.close()


def message_header(way, number, origin: str, destination):
    if way == "vuelta":
        origin, destination = destination, origin
    billetes = "billetes"
    if number == 1:
        billetes = "billete"
    return dedent(f"""He encontrado {number} {billetes} de {origin.title()} \
        a {destination.title()} con los parámetros introducidos:\n\n""")


def tickets_df_message(df: pd.DataFrame, watcher_params: dict, return_):
    df['time_of_departure'] = df['time_of_departure'].dt.strftime('%H:%M')
    df['time_of_arrival'] = df['time_of_arrival'].dt.strftime('%H:%M')

    if not return_:
        df['price'] = df['price'] * 1.25
    df['price'] = df['price'].round(2)

    message = message_header(df['direction'].iloc[0], len(df),
                             watcher_params['origin_station'], watcher_params['destination_station'])
    for index, row in df.iterrows():
        message += f"🚆 Tren {row['train_type']} - 🕒 {row['time_of_departure']} - {row['time_of_arrival']} 🕙 - {row['price']} €\n"
    return message
