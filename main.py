from scraper import RenfeScraper

bot = RenfeScraper()
bot.search_stations("Málaga María Zambrano", "Sevilla-Santa Justa")
bot.search_dates("18-07-2023 00:00", "20-07-2023 00:00")
bot.get_results()
