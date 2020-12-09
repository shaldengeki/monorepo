FROM node:alpine

ENV PORT=5001
ENV REACT_APP_API_HOST=192.168.1.5
ENV REACT_APP_API_PORT=5000

WORKDIR /usr/src/app

COPY package-lock.json ./
COPY package.json ./

RUN npm install

COPY . .

RUN npm run build

CMD npm run start
