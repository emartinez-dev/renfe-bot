from scraper.scraper import RenfeScraper, RenfeData

ride_data = RenfeData("02/11/2023", "03/11/2023",
                      "CÓRDOBA", "SEVILLA-SANTA JUSTA")

scraper = RenfeScraper()
scraper.find_trains(ride_data)

for i in range(5):
    scraper.get_results()
    print(scraper)
    scraper.wait_and_refresh(5)

scraper.close()
