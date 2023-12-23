import requests
from textwrap import dedent
import configparser


def bot_config():
    config = configparser.ConfigParser()
    config.read("config.ini")

    if 'Telegram' not in config:
        print(dedent("""\
        Hola! Voy a ayudarte a configurar tu propio RenfeBot para que te avise
        cuando haya billetes disponibles para el trayecto que quieras.

        Antes de nada y por motivos obvios, necesitas tener una cuenta de Telegram antes
        de crear un bot de Telegram.

        Para crear el bot, debes ir a este enlace y empezar una conversación con el
        asistente -> https://t.me/botfather
        Una vez empieces la conversación, el asistente te irá guiando durante todo el
        proceso, solo tienes que escribir /newbot para crear uno

        Después de introducir el nombre y su nombre de usuario, el asistente te dará
        tanto el token de acceso a la API como el nombre de usuario del bot. Guarda la URL
        para poder interactuar con él e introduce el token a continuación.

        Puede que al correr el script en Docker, no te deje introducir el token, puedes saltarte
        este paso y escribirlo directamente en el archivo config.ini con este formato:
        ---
            [Telegram]
            secret_token=123456789:ABCdefGhIjKlmNopQrsTuvWxYz
        ---
        """))
        config['Telegram'] = {}

    if 'secret_token' not in config['Telegram']:
        while 'secret_token' not in config['Telegram']:
            token = input("Introduce el token de tu bot: ")
            url = f"https://api.telegram.org/bot{token}/getMe"

            r = requests.get(url)

            if r.status_code == 200:
                print("Bot creado correctamente!")
                config['Telegram']['secret_token'] = token
            elif r.status_code == 401:
                print("Token incorrecto, vuelve a intentarlo")
            else:
                print("Ha ocurrido un error, vuelve a intentarlo")

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def get_token():
    config = configparser.ConfigParser()
    config.read("config.ini")

    if 'Telegram' not in config or 'secret_token' not in config['Telegram']:
        bot_config()
        config.read("config.ini")

    return config['Telegram']['secret_token']
