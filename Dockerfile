FROM python:3.9-slim-buster

ARG GIT_ACCESS_TOKEN

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install git \
  && apt-get clean

RUN git config --global url."https://${GIT_ACCESS_TOKEN}@github.com".insteadOf "ssh://git@github.com"
RUN git config --global url."https://${GIT_ACCESS_TOKEN}@github.com".insteadOf "https://github.com"

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY app/ /app/app
COPY .env /app/.env
