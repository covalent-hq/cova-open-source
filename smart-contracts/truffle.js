/*
 * NB: since truffle-hdwallet-provider 0.0.5 you must wrap HDWallet providers in a 
 * function when declaring them. Failure to do so will cause commands to hang. ex:
 * ```
 * mainnet: {
 *     provider: function() { 
 *       return new HDWalletProvider(mnemonic, 'https://mainnet.infura.io/<infura-key>') 
 *     },
 *     network_id: '1',
 *     gas: 4500000,
 *     gasPrice: 10000000000,
 *   },
 */

const fs = require('fs')
const PrivateKeyProvider = require("truffle-privatekey-provider");
var config = JSON.parse(fs.readFileSync('./secret-config.json'))

module.exports = {
  networks: {
    cova: {
      provider: new PrivateKeyProvider(config.privateKey, config.url),
      network_id: '*'
    }
  }
};
