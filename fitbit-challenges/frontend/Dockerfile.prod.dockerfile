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

RUN npm run build

RUN npm run tailwind:css

FROM nginx:1.24-alpine

COPY --from=0 /usr/src/app/build /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
