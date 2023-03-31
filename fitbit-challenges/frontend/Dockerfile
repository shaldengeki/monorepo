FROM node:alpine

ENV PORT=5001
ENV REACT_APP_API_HOST=127.0.0.1
ENV REACT_APP_API_PORT=5000
ENV REACT_APP_API_PROTOCOL=http

WORKDIR /usr/src/app

COPY package-lock.json ./
COPY package.json ./

RUN npm install

COPY . .

RUN npm run tailwind:css

CMD npm run start
