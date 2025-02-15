FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
