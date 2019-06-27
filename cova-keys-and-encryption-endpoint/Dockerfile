FROM node:8
WORKDIR /usr/src/cred_encryption

COPY package*.json ./
RUN npm install 

COPY . .

EXPOSE 5002
CMD ["npm", "start"]
