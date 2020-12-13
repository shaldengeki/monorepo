FROM python:3.9-alpine

RUN apk update && \
    apk add docker-cli

WORKDIR /usr/src/app

ENV API_HOST=api
ENV API_PORT=5000

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ./wait-for $API_HOST:$API_PORT -- python worker.py
