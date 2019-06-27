var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider(process.env.RPC_URL));
var util = require('ethereumjs-util');
var tx = require('ethereumjs-tx');

const makeRawTransaction = async (_contractAddress, _methodCallData, _privateKey) => {
  try{
    console.log(_contractAddress, _methodCallData, _privateKey)
    var from = util.bufferToHex(util.privateToAddress('0x' + _privateKey))
    var txCount = await web3.eth.getTransactionCount(from)
    console.log('got tx count => ', txCount)
    var rawTransaction = {
      "from": from,
      "nonce": web3.utils.toHex(txCount),
      "gasPrice": web3.utils.toHex(web3.utils.toWei('10', 'gwei')),
      "gasLimit": web3.utils.toHex(6712353),
      "to": _contractAddress,
      "data": _methodCallData
    };

    const privateKeyBuffer = new Buffer(_privateKey, 'hex');
    var etx = new tx(rawTransaction);
    etx.sign(privateKeyBuffer);
    var serializedTx = etx.serialize();
    var reciept = await web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
    return {
      error: false,
      reciept: reciept
    }
  }
  catch(e){
    console.log(e);
    return {
      error: true,
      desc: e
    }
  }
}

const sendEther = async (_toAddress, _amount, _privateKey) => {
  try{
    var from = util.bufferToHex(util.privateToAddress('0x' + _privateKey))
    var txCount = await web3.eth.getTransactionCount(from)
  
    console.log(txCount)
    var rawTransaction = {
      "from": from,
      "nonce": web3.utils.toHex(txCount),
      "gasPrice": web3.utils.toHex(web3.utils.toWei('10', 'gwei')),
      "gasLimit": web3.utils.toHex(6712353),
      "to": _toAddress,
      "value": web3.utils.toHex(web3.utils.toWei(_amount, "ether")),
    };

    const privateKeyBuffer = new Buffer(_privateKey, 'hex');
    var etx = new tx(rawTransaction);
    etx.sign(privateKeyBuffer);
    var serializedTx = etx.serialize();
    var reciept = await web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
    return {
      error: false,
      reciept: reciept
    }
  }
  catch(e){
    console.log(e);
    return {
      error: true,
      desc: e
    }
  }
}



module.exports = {
  makeRawTransaction,
  sendEther
}
