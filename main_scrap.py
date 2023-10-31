from scraper.scraper import RenfeScraper, RenfeData
from watcher.watcher import Watcher

# we have to create this from user
"""
ride_data = RenfeData("31/10/2023", "CÓRDOBA", "VITORIA/GASTEIZ")

# Example usage for just scraping the website
scraper = RenfeScraper()
scraper.find_trains(ride_data)

for i in range(1):
    scraper.get_results()
    print(scraper.train_data)
    scraper.wait_and_refresh(5)

scraper.stop()
"""

filter = {
    "origin_departure_time": "07.20",
    "origin_arrival_time": "16.00",
    "return_departure_time": "00.00",
    "return_arrival_time": "20.59",
    "max_price": 100,
}

query = RenfeData("SEVILLA-SANTA JUSTA", "MÁLAGA MARÍA ZAMBRANO", "01/11/2023")
scrap = Watcher(query, filter)
scrap.loop()
trains = scrap.get_tickets()
print(trains)
