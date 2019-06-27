FROM node:8
WORKDIR /usr/src/blockchain-api

COPY package*.json ./
RUN npm install 

COPY . .

RUN npm install -g truffle

EXPOSE 5000

CMD ["npm", "start"]
