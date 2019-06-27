var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://ganache:8545'));
const fs = require('fs');
const artifacts = JSON.parse(fs.readFileSync('./build/contracts/Faucet.json', 'utf8'))
const abiArray = artifacts.abi

const contractAddress = artifacts.networks[Object.keys(artifacts.networks)[0]].address
console.log('faucet', JSON.stringify(artifacts.networks), 'Running at: ', contractAddress)

const express = require('express')
const router = express.Router()
const contract = new web3.eth.Contract(abiArray, contractAddress);

const eth_tx = require('../controllers/eth-tx')
const bdb = require('../controllers/bdb')
const rsa = require('../controllers/rsa')

function verify(header){
  try{
    if(header == process.env.TOKEN){
      return true;
    }
    else{
      return false;
    }
  }
  catch(e){
    return false;
  }
}


router.get('/lastFunded/:user', (req, res) => {
  contract.methods.lastFunded(req.params.user).call()
  .then((result) => {
    res.send(result)
  })
})

router.get('/fund/:fromPrivateKey/:user', (req, res) => {
  if(verify(req.headers['authorization']) == false){
    res.sendStatus(403);
  }
  else {
    eth_tx.makeRawTransaction(contractAddress, contract.methods.fund(req.params.user).encodeABI(req.param), req.params.fromPrivateKey)
    .then((result) => {
      res.send(result)
    });
  }
})

router.get('/setAmount/:fromPrivateKey/:amount', (req, res) => {
  var amount = web3.utils.toWei(req.params.amount, 'ether')
  eth_tx.makeRawTransaction(contractAddress, contract.methods.setAmount(amount).encodeABI(), req.params.fromPrivateKey)
  .then((result) => {
    res.send(result)
  });
})

router.get('/createnfund', (req, res) => {
  try {
    if(verify(req.headers['authorization']) == false){
      res.sendStatus(403);
    }
    else {
      var final_result = {}
      var account;
      try{
        account = web3.eth.accounts.create()
        final_result.eth_cred = account;
        final_result.bdb_cred = bdb.get_bdb_cred();
        final_result.rsa_cred = rsa.get_rsa_cred();
        eth_tx.makeRawTransaction(contractAddress, contract.methods.fund(account.address).encodeABI(), process.env.PRIVATE_KEY.substring(2))
        .then((result) => {
          if(result.error == false){
            final_result.cova_tx_hash = result.reciept;
            eth_tx.sendEther(account.address, '1', process.env.PRIVATE_KEY.substring(2))
            .then((result) => {
              final_result.eth_tx_hash = result.reciept;
              res.send(final_result);
            });
          }
          else{
            res.send(result)
          }
        });
      }
      catch(e){
        res.send(e)
      }
    }
  }
  catch(e){
    res.send(e)
  }
})


module.exports = router
