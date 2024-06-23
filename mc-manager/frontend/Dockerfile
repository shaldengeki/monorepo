FROM node:alpine

ENV PORT=5001
ENV REACT_APP_API_SCHEME=http
ENV REACT_APP_API_HOST=localhost
ENV REACT_APP_API_PORT=5000
ENV REACT_APP_API_PATH=graphql

WORKDIR /usr/src/app

RUN apk update && \
    apk add yarn

COPY yarn.lock ./
COPY package.json ./

RUN yarn install

COPY . .

RUN yarn run craco build

CMD yarn run craco start
