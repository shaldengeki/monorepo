FROM python:3.9-alpine

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add docker-cli

WORKDIR /usr/src/app

ENV API_HOST=api
ENV API_PORT=5000
ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV HOST_PATH=/var/minecraft
ENV S3_BUCKET=

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python worker.py
