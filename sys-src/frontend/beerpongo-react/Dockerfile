FROM node:14.17.3 as build-node

RUN mkdir /app
COPY . /app
WORKDIR /app

ARG backend_url 
ENV REACT_APP_BACKEND_URL=$backend_url
RUN npm install
ENV PATH /node_modules/.bin:$PATH
RUN npm run build


FROM nginx:stable-alpine

COPY --from=build-node /app/build /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx" , "-g", "daemon off;"]