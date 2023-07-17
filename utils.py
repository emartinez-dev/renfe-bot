from datetime import datetime, timedelta
import pandas as pd

def convert_date_string(date_str):
	# Define the format of the input date string
	date_format = "%d-%m-%Y %H:%M"
	# Convert the date string to a datetime object
	date_obj = datetime.strptime(date_str, date_format)
	return date_obj

def calculate_duration(start_time, end_time):
    start = datetime.strptime(start_time, '%H.%M').time()
    end = datetime.strptime(end_time, '%H.%M').time()

    # Handling cases where the arrival time is on the next day
    if end < start:
        end = datetime.combine(datetime.min.date(), end)
        end += timedelta(days=1)

    duration = (datetime.combine(datetime.min.date(), end) - datetime.combine(datetime.min.date(), start)).total_seconds() / 3600
    return duration

def format_time(time):
	return pd.to_datetime(time, format='%H.%M')
