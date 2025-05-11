FROM node:20

WORKDIR /app
COPY frontend/ /app
RUN npm install

RUN npm install vue-router@4

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
