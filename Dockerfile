FROM mcr.microsoft.com/playwright:v1.49.0-jammy

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y python3-pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "renfe-bot.py"]
