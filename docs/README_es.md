# renfe-bot

[![CI](https://github.com/emartinez-dev/renfe-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/emartinez-dev/renfe-bot/actions/workflows/ci.yml)
[![Nightly Tests](https://github.com/emartinez-dev/renfe-bot/actions/workflows/nightly-tests.yml/badge.svg)](https://github.com/emartinez-dev/renfe-bot/actions/workflows/nightly-tests.yml)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Femartinez-dev%2Frenfe-bot%2Fmaster%2Fpyproject.toml)
[![codecov](https://codecov.io/gh/emartinez-dev/renfe-bot/graph/badge.svg?token=L39OAEL5MD)](https://codecov.io/gh/emartinez-dev/renfe-bot)
![license](https://img.shields.io/github/license/emartinez-dev/renfe-bot.svg)

| Versión de Python soportada | Plataformas soportadas |
|-----------------------------|------------------------|
| ![Python >= 3.12](https://img.shields.io/badge/python-%3E%3D%203.12-blue.svg) | ![Linux](https://img.shields.io/badge/platform-Linux-blue.svg) ![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg) ![Windows](https://img.shields.io/badge/platform-Windows-brightgreen.svg) |

_You can also read this in [English](https://github.com/emartinez-dev/renfe-bot/blob/master/README.md)_

## Descripción

Renfe-bot es un bot de Telegram diseñado para ayudar a los usuarios a comprar billetes de tren
de Renfe, el principal operador ferroviario de España. El bot monitoriza la disponibilidad
especialmente en situaciones en las que los billetes se agotan y sólo se pueden comprar
cuando alguien cancela su reserva, y avisa rápidamente a los usuarios cuando hay billetes
disponibles. El bot ahora es compatible con una interfaz de chatbot de Telegram
para mejorar la interacción con el usuario.

La gestión de errores no es perfecta, por lo que si te encuentras con algún problema, reintentar el comando
debería funcionar. Si el problema persiste, abre una incidencia en GitHub.


## Como utilizar

### Opción 1: correr el programa localmente en tu ordenador

#### Requisitos

Este proyecto requiere al menos Python 3.12, y funciona en macOS, Linux y
Windows.

#### Instalación

Sigue los siguientes pasos para instalar y configurar Renfe-bot:

Clona este repositorio en tu máquina local
```bash
git clone git@github.com:emartinez-dev/renfe-bot.git
```

Instala las dependencias necesarias utilizando el siguiente comando
```bash
pip install -r requirements.txt
```

Ejecuta el bot con este comando
```bash
PYTHONPATH=src/ python src/bot.py
```

o este otro si estás en la terminal de Windows
``bash
setx PYTHONPATH src/
python src/bot.py
```

Todo lo que sea necesario, como la clave API, se te pedirá cuando ejecutes el bot por primera vez.


### Opción B: Correrlo en local como un contenedor de Docker

#### Requisitos

Para ejecutar esto en Docker, sólo necesitará tener una instalación válida de Docker,
todo lo demás se proporciona en el Dockerfile.

#### Instalación

Primero necesitas construir la imagen, hazlo con el siguiente comando:

```bash
docker build -t renfe-bot .
```

Cuando la imagen termine el build, ya se puede ejecutar con el siguiente comando:

```bash
docker run -it -v $(pwd):/app renfe-bot
```

O si usas Windows:

```bat
docker run -it -v %cd%:/app renfe-bot
```


## Uso


Para utilizar el bot, envía un mensaje a tu bot en Telegram. Tienes que proporcionar
datos como las estaciones de origen y destino, y las fechas. El bot monitorizará
la disponibilidad de billetes y te notificará inmediatamente cuando haya un billete
disponible para tu viaje.

## Contribución

Este proyecto es de código abierto y las contribuciones son más que bienvenidas. Si quieres
contribuir al proyecto, siga estos pasos:

1. Fork el repositorio.
2. Crea una nueva rama para tus cambios.
3. Realice sus cambios.
4. Pushea los cambios al fork.
5. Envía una pull request con una descripción de los cambios.

Antes de fusionarlos, todos los cambios se probarán para garantizar que funcionan correctamente.
Las contribuciones no se limitan a cambios en el código, cualquier sugerencia o feedback son igualmente valiosas.

## Licencia

Este proyecto está licenciado bajo los términos de la [MIT License](https://opensource.org/license/mit/).

La Licencia MIT es una licencia permisiva que permite la reutilización de software dentro de
software propietario siempre que todas las copias del software licenciado incluyan una
copia de los términos de la Licencia MIT y el aviso de copyright.

Esto significa que usted es libre de utilizar, copiar, modificar, fusionar, publicar, distribuir
sublicenciar y/o vender copias del software, siempre que incluya la atribución
atribución necesaria y proporcione una copia de la licencia MIT.

Puede consultar el texto completo de la licencia en el archivo LICENSE.

