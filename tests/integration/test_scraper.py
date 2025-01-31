from datetime import datetime, timedelta

from scraper import Scraper
from storage import StationsStorage

today = datetime.now()

origin = StationsStorage.get_station("MADRID (TODAS)")
destination = StationsStorage.get_station("BARCELONA (TODAS)")
departure_date = today + timedelta(days=2)
return_date = today + timedelta(days=3)

scraper = Scraper(origin, destination, departure_date, return_date)

trains = scraper.get_trainrides()

assert len(trains) > 0, "There are no trains from Madrid to Barcelona (which is impossible)"
