FROM python:3.12

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps

EXPOSE 80

CMD ["python", "main_scrap.py"]
