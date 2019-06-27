var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://ganache:8545'));

function get_eth_cred(){
    cred = web3.eth.accounts.create()
    return {
        address: cred.address,
        privateKey: cred.privateKey
    }
}

module.exports = {
    get_eth_cred
}