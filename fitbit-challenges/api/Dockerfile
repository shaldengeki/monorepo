FROM python:3-alpine

EXPOSE 5000/tcp

RUN apk update && \
    apk add --virtual build-deps gcc git python3-dev musl-dev && \
    apk add postgresql-dev postgresql-client

WORKDIR /usr/src/app

ENV FLASK_APP=app.py
ENV PORT=5000
ENV FRONTEND_PROTOCOL=http
ENV FRONTEND_HOST=frontend
ENV FRONTEND_PORT=5001
ENV DB_HOST=pg
ENV DB_USERNAME=admin
ENV DB_PASSWORD=development
ENV DATABASE_NAME=api_development
ENV FITBIT_CLIENT_SECRET=testing
ENV FITBIT_VERIFICATION_CODE=testing

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ./scripts/wait-for-postgres.sh -- flask run --host 0.0.0.0 --port $PORT
