FROM node:alpine

ENV PORT=5001
ENV REACT_APP_API_SCHEME=http
ENV REACT_APP_API_HOST=localhost
ENV REACT_APP_API_PORT=5000
ENV REACT_APP_API_PATH=graphql

WORKDIR /usr/src/app

COPY package-lock.json ./
COPY package.json ./

RUN npm install

COPY . .

RUN npm run build

CMD npm run start
