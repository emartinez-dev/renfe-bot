# renfe-bot

**Read this in [English](../README.md)**

## Descripción

Renfe-bot es un bot de Telegram diseñado para ayudar a los usuarios a comprar
billetes de tren de Renfe, el principal operador ferroviario de España. El bot
monitorea la disponibilidad de billetes, especialmente en situaciones en las que
están agotados y solo se vuelven a estar disponibles cuando alguien cancela su
reserva. Notifica rápidamente a los usuarios cuando hay billetes disponibles
para comprar. El bot ahora admite una interfaz de chatbot de Telegram para una
interacción mejorada con el usuario.

El manejo de errores no es perfecto, por lo que si encuentras algún problema,
reintando el comando o utilizando /reintentar debería funcionar. Si el problema
persiste, por favor abre un ticket en GitHub.

## Como utilizar el bot

### Opción A: Correrlo Normalmente en tu ordenador

#### Requisitos

Este proyecto ha sido desarrollado utilizando la última versión de Python disponible ahora mismo
(`3.12.7`). Puede que funcione con versiones anteriores de Python 3, pero no lo he probado.

Las dependencias requeridas para ejecutar este proyecto están incluidas en el
archivo `requirements.txt`. Para instalar los requisitos, usa el siguiente
comando:

```bash
pip install -r requirements.txt
```

#### Instalación

Sigue los siguientes pasos para instalar y configurar el Renfe-bot:

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias requeridas utilizando el comando mencionado en la
   sección 'Requisitos'.
3. Ejecuta el bot ejecutándolo con (`python src/bot.py`).
4. Cualquier dato requerido, como la clave API, se solicitará cuando ejecutes el
   bot por primera vez.

### Opción B: Correrlo en un container de Docker

#### Requisitos

Para correrlo en Docker, solo necesitas tenerlo instalado, todo lo demás viene
en el Dockerfile.

> [!IMPORTANT]
> Es posible que tengas que añadir `sudo` antes de cada comando de
> Docker, también puedes añadir tu usuario al grupo `docker`, revisa [este documento]
> (https://docs.docker.com/engine/install/linux-postinstall/).

#### Instalación

Primero hay que construir la imagen, lo hacemos con el siguiente comando:

```bash
docker build -t renfe-bot .
```

Cuando la imagen termine de construirse, podemos correrla con el siguiente comando:

```bash
docker run -it -v $(pwd):/app renfe-bot
```

O si estás utilizando Windows:

```bat
docker run -it -v %cd%:/app renfe-bot
```

## Uso

Para usar el bot, envía un mensaje a tu bot en Telegram. Necesitarás
proporcionar datos como las estaciones de origen y destino, y las fechas. El bot
monitoreará la disponibilidad de billetes y te notificará inmediatamente cuando
haya un billete disponible para tu viaje.

## Contribuciones

Este proyecto es de código abierto y las contribuciones son muy bienvenidas. Si
deseas contribuir al proyecto, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama para tus cambios.
3. Realiza tus cambios.
4. Envía tus cambios a tu fork.
5. Envía una pull request con una descripción de los cambios.

Antes de fusionar, todos los cambios serán probados para asegurar que funcionan
correctamente. Las contribuciones no se limitan a cambios de código; abrir
problemas o proporcionar sugerencias son igualmente valiosos.

## Licencia

Este proyecto está licenciado bajo los términos de la [Licencia
MIT](https://opensource.org/license/mit/).

La Licencia MIT es una licencia permisiva que permite la reutilización de
software dentro del software propietario siempre que todas las copias del
software licenciado incluyan una copia de los términos de la Licencia MIT y el
aviso de derechos de autor.

Esto significa que eres libre de usar, copiar, modificar, fusionar, publicar,
distribuir, sublicenciar y/o vender copias del software, siempre que incluyas la
atribución necesaria y proporciona una copia de la licencia MIT.

Puedes ver el texto completo de la licencia en el archivo LICENSE.
