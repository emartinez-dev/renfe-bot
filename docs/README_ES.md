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

## Requisitos

Las dependencias requeridas para ejecutar este proyecto están incluidas en el
archivo `requirements.txt`. Para instalar los requisitos, usa el siguiente
comando:

```bash
pip install -r requirements.txt
```

## Instalación

Sigue los siguientes pasos para instalar y configurar el Renfe-bot:

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias requeridas utilizando el comando mencionado en la
   sección 'Requisitos'.
3. Ejecuta el bot ejecutándolo (`python bot/renfebot.py`) en el directorio raíz
   del proyecto.
4. Cualquier dato requerido, como la clave API, se solicitará cuando ejecutes el
   bot por primera vez.

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

## TODO

- [ ] Cambiar el driver para usar el modo sin cabeza
- [x] Implementar bot de Telegram
- [x] Añadir instrucciones de instalación
- [x] Añadir instrucciones de uso
