FROM python:3.7-alpine

RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev

WORKDIR /usr/src/app

ENV FLASK_APP=app.py
ENV PORT=5000

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD flask run --host 0.0.0.0 --port $PORT