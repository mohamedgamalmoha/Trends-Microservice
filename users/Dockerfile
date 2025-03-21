FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONBUFFERED = 1

WORKDIR /app

RUN apt-get update && apt-get install -y git && apt-get install -y postgresql-client

COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

CMD chmod +x /scripts/startup.sh && /scripts/startup.sh
