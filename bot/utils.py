import Levenshtein
import json
import os

def sanitize_station_input(user_input:str):
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
