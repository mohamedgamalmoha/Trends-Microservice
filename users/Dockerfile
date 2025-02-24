FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

CMD ["alembic", "-c", "app/alembic.ini", "revision", "--autogenerate"]
CMD ["alembic", "-c", "app/alembic.ini", "upgrade", "head"]
