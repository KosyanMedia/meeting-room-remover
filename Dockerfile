FROM python:3.8-buster

ENV PYTHONPATH="/app"

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y cron

RUN pip install --upgrade pip
RUN pip install pipenv

COPY ./Pipfile* ./
RUN pipenv install
COPY . .

ADD crontab /etc/cron.d/meeting-room-remover
RUN chmod 0644 /etc/cron.d/meeting-room-remover

ENTRYPOINT []
