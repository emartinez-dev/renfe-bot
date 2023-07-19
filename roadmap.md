# Roadmap for RenfeBot

High-level overview of how the bot will be structured:

User -> Filter into Telegram Bot -> Task Queue ---> Scrapers -> Informer -> User

I don't know if I am going to deploy it and allow other people to use it,
everybody should host their own I think

- Hosting: The server should be capable of running multiple concurrent tasks. A
cloud hosting provider like AWS, Google Cloud, or Azure could work. For a
simpler and cheaper alternative, a VPS from a provider like DigitalOcean or
Linode could also be suitable.

- Web Framework: I will likely need a web framework to handle incoming user
requests. Something like Flask or Django could work for this. This web
application will receive the user requests, add them to a queue, and manage
starting the scraping tasks.

- Task Queue: For managing the queue of user requests, I could use a task queue
like Celery. Celery lets you distribute tasks across multiple worker processes,
which can be running on different machines if needed.

- Concurrent Scraping: For running the scrapers concurrently, I will want to use
something like threading or multiprocessing in Python, or even asynchronous
programming with asyncio. With Celery, I can start a new task for each user
request.

- Error Handling and Retries: With the tasks running in Celery, I can easily
configure it to handle failures and retries. I can specify a maximum number of
retries and a delay between retries.

- Telegram Notifications: I can keep your Telegram notification logic in the
Informer class. Each task will have its own instance of the Informer class, and
can send notifications independently of the others.
