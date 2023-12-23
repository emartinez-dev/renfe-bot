# renfe-bot

**También puedes leer esto en [Español](./docs/README_ES.md)**

## Description

Renfe-bot is a Telegram bot designed to assist users in purchasing train tickets
from Renfe, the main railway operator in Spain. The bot monitors ticket
availability, especially in situations when tickets are sold out and only become
available when someone cancels their reservation. It promptly notifies users
when there are tickets available for purchase. The bot now supports a Telegram
chatbot interface for enhanced user interaction.

The error handling is not perfect, so if you encounter any issues, retrying the
command should work. If the issue persists, please open an issue on GitHub.

## Requirements

The required dependencies to run this project are included in the
`requirements.txt` file. To install the requirements, use the following command:

```bash
pip install -r requirements.txt
```

## Installation

Follow the below steps to install and set up the Renfe-bot:

1. Clone this repository to your local machine.
2. Install the required dependencies using the command mentioned in the
   'Requirements' section.
3. Install playwright and its dependencies with the following commands: `playwright install; playwright install-deps`
4. Run the bot by executing it (`python renfebot.py`) in the root
   directory of the project.
5. Anything required like the API key will be prompted for when you run the bot
   for the first time.

## Usage

To use the bot, send a message to your bot on Telegram. You need to provide
inputs such as origin and destination stations, and dates. The bot will monitor
the ticket availability and notify you immediately when there's a ticket
available for your journey.

## Contributing

This project is open source and contributions are very much welcomed. If you
would like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes.
4. Push your changes to your fork.
5. Submit a pull request with a description of the changes.

Before merging, all changes will be tested to ensure they function correctly.
Contributions are not limited to code changes; opening issues or providing
suggestions are equally valuable.

## License

This project is licensed under the terms of the [MIT
License](https://opensource.org/license/mit/).

The MIT License is a permissive license that allows for reuse of software within
proprietary software provided that all copies of the licensed software include a
copy of the MIT License terms and the copyright notice.

This means that you are free to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the software, as long as you include the
necessary attribution and provide a copy of the MIT license.

You can see the full license text in the LICENSE file.
