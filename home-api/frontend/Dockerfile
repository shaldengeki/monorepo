FROM node:alpine

WORKDIR /usr/src/app

COPY package-lock.json ./

RUN npm install

COPY . .

CMD npm start