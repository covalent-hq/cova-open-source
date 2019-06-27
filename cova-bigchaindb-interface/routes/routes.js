var bdb = require('../bigchaindb/bdb')
var driver = require('bigchaindb-driver')
var express = require('express');
var router = express.Router()
var request = require('async-request')


router.post('/register_asset', (req, res) => {
  var asset = {}

  var keypair = {
    publicKey: req.body.bdb_public_key,
    privateKey: req.body.bdb_private_key
  }
  
  console.log(req.body);
  for (var property in req.body) {
      if (req.body.hasOwnProperty(property)) {
          if(property.startsWith('keyfrag')){
            asset[property] = req.body[property]
          }
      }
  }

  metadata = {
    type: 'dataset_v0.01',
    metadata: {
      data_hash: req.body.data_hash,
      data_link: req.body.data_link
    }
  }

  bdb.register_asset(asset, metadata, keypair)
  .then((result) => {
      res.send(result)
  })
})

router.get('/get_keyfrag/:data_hash/:id', (req, res) => {
  bdb.searchMetadatas(req.params.data_hash)
  .then((result) => {
      if(result.success == false){
        res.send(result);
      }
      var txID = result.result[0].id;
      bdb.get_transaction_by_id(txID)
      .then((tx_result) => {
        if(tx_result.success == false){
          res.send(tx_result);
        }
        tx = tx_result.transaction
        console.log(tx)
        console.log(tx.asset.data['keyfrag_1'])
        console.log()
        output = {
          success: true,
          asset_id: tx.asset.id,
          keyfrag: tx.asset.data['keyfrag_' + req.params.id],
          metadata: tx.metadata
        }
        res.send(output);
      })
  })
})

router.post('/register_task', (req, res) => {
  var keypair = {
    publicKey: req.body.bdb_public_key,
    privateKey: req.body.bdb_private_key
  }
  var asset = { task_id: req.body.task_id }
  var metadata = { type: 'completed_task_v0.01' }
  bdb.register_asset(asset, metadata, keypair)
  .then((result) => {
      res.send(result)
  })
})

router.get('/find_task/:task_id', (req, res) => {
  bdb.searchAssets(req.params.task_id)
  .then((result) => {
      if(result.success == false){
        res.send(result);
      }
      else{
        var ret = { error: false, found: true }
        if(result.result.length == 0) {
          ret.found = false;
        }
        res.send(ret);
      }
  })
})




module.exports = router
