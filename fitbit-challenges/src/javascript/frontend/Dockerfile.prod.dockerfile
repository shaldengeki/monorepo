FROM node:alpine

ENV PORT=5001
ENV REACT_APP_API_HOST=api.fitbit.ouguo.us
ENV REACT_APP_API_PORT=443
ENV REACT_APP_API_PROTOCOL=https

WORKDIR /usr/src/app

COPY package-lock.json ./
COPY package.json ./

RUN npm install

COPY .env.production ./
COPY . .

RUN npm run tailwind:css

RUN npm run build:prod

FROM nginx:1.24-alpine

COPY --from=0 /usr/src/app/build /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
