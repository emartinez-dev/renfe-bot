from scraper.scraper import RenfeScraper, RenfeData
from watcher.watcher import Watcher

import telebot
from bot.credentials import get_token

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
    "origin_departure_time": "15.00",
    "origin_arrival_time": "21.00",
    "return_departure_time": "08.00",
    "return_arrival_time": "13.59",
    "max_price": 30,
}

TOKEN = get_token()
bot = telebot.TeleBot(TOKEN)
print("Ya estoy corriendo")


@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Buscando trenes...")

    query = RenfeData("MÁLAGA MARÍA ZAMBRANO", "SEVILLA-SANTA JUSTA", "05/11/2023")
    scrap = Watcher(query, filter)
    try:
        scrap.loop()
        trains = scrap.get_tickets()
        bot.send_message(message.chat.id, "He encontrado algo!")
        print(trains)
    except Exception as e:
        bot.send_message(message.chat.id, "Algo ha fallado, info:")
        bot.send_message(message.chat.id, e.__str__())


bot.polling()
