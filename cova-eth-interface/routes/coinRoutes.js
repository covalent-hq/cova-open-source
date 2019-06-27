var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://ganache:8545'));

const fs = require('fs');
const artifacts = JSON.parse(fs.readFileSync('./build/contracts/CovaToken.json', 'utf8'))
const abiArray = artifacts.abi

const contractAddress = artifacts.networks[Object.keys(artifacts.networks)[0]].address

console.log('covaToken', JSON.stringify(artifacts.networks), 'Running at: ', contractAddress)
const express = require('express')
const router = express.Router()
const contract = new web3.eth.Contract(abiArray, contractAddress);

const eth_tx = require('../controllers/eth-tx')

router.get('/totalSupply', (req, res) => {
  contract.methods.totalSupply().call()
  .then((result) => {
    res.send(web3.utils.fromWei(result, 'ether'))
  })
})

router.get('/transfer/:fromPrivateKey/:toAddress/:amount', (req, res) => {
  var amount = web3.utils.toWei(req.params.amount, 'ether')
  eth_tx.makeRawTransaction(contractAddress, contract.methods.transfer(req.params.toAddress, amount).encodeABI(),  req.params.fromPrivateKey)
  .then((result) => {
    res.send(result)
  });
})

router.get('/approve/:fromPrivateKey/:toAddress/:amount', (req, res) => {
  var amount = web3.utils.toWei(req.params.amount, 'ether')
  eth_tx.makeRawTransaction(contractAddress, contract.methods.approve(req.params.toAddress, amount).encodeABI(),  req.params.fromPrivateKey)
  .then((result) => {
    res.send(result)
  });
})

router.get('/transferFrom/:fromPrivateKey/:fromAddress/:toAddress/:amount', (req, res) => {
  var amount = web3.utils.toWei(req.params.amount, 'ether')
  eth_tx.makeRawTransaction(contractAddress, contract.methods.transferFrom(req.params.fromAddress, req.params.toAddress, amount).encodeABI(),  req.params.fromPrivateKey)
  .then((result) => {
    res.send(result)
  });
})


router.get('/balance/:address', (req, res) => {
  contract.methods.balanceOf(req.params.address).call()
  .then((result) => {
    res.send(web3.utils.fromWei(result, 'ether'))
  })
})

router.get('/allowance/:fromAddress/:toAddress', (req, res) => {
  contract.methods.balanceOf(req.params.fromAddress, toAddress).call()
  .then((result) => {
    res.send(result)
  })
})


module.exports = router
