FROM node:8
WORKDIR /usr/src/bigchaindb

COPY package*.json ./
RUN npm install 

COPY . .

EXPOSE 5001
CMD ["npm", "start"]
