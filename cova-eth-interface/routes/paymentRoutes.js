var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://ganache:8545'));

const fs = require('fs');
const artifacts = JSON.parse(fs.readFileSync('./build/contracts/Agreements.json', 'utf8'))
const abiArray = artifacts.abi

const contractAddress = artifacts.networks[Object.keys(artifacts.networks)[0]].address

console.log('payment', JSON.stringify(artifacts.networks), 'Running at: ', contractAddress)
const express = require('express')
const router = express.Router()
const contract = new web3.eth.Contract(abiArray, contractAddress);
const eth_tx = require('../controllers/eth-tx')

router.get('/registerDataset/:datasetId/:fromPrivateKey', (req, res) => {
  eth_tx.makeRawTransaction(contractAddress, contract.methods.registerDataset(req.params.datasetId).encodeABI(),  req.params.fromPrivateKey)
  .then((result) => {
    res.send(result)
    console.log(result)
  });
})

router.get('/checkDataset/:datasetId', (req, res) => {
  contract.methods.checkDataset(req.params.datasetId).call()
  .then((result) => {
    res.send(result)
  })
})

router.get('/createAgreement/:taskId/:fromPrivateKey/:datasetId/:amount/:aliveTime', (req, res) => {
  var amount = web3.utils.toWei(req.params.amount, 'ether')
  eth_tx.makeRawTransaction(contractAddress, contract.methods.createAgreement(req.params.taskId, req.params.datasetId, amount, parseInt(req.params.aliveTime)).encodeABI(),  req.params.fromPrivateKey)
  .then((result) => {
    console.log(result)
    res.send(result)
  });
})

router.get('/seeAgreement/:taskId', (req, res) => {
  contract.methods.seeAgreement(req.params.taskId).call()
  .then((result) => {
    res.send(result)
  })
})

router.get('/seeAddress', (req, res) => {
  contract.methods.seeAddress().call()
  .then((result) => {
    res.send(result)
  })
})

module.exports = router
