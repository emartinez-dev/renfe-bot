FROM python:3.12.7

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y python3-pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "src/bot.py"]
