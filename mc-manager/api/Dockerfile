FROM python:3.9-alpine

EXPOSE 5000/tcp

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-dev

WORKDIR /usr/src/app

ENV FLASK_APP=app.py
ENV PORT=5000
ENV FRONTEND_HOST=home_frontend
ENV FRONTEND_PORT=5001

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD flask run --host 0.0.0.0 --port $PORT
