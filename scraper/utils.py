from datetime import datetime, timedelta
import pandas as pd

def str_to_dt(dt_str):
	dt_format = "%d-%m-%Y %H:%M"
	return datetime.strptime(dt_str, dt_format)

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
