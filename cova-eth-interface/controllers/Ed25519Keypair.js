// Copyright BigchainDB GmbH and BigchainDB contributors
// SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
// Code is Apache-2.0 and docs are CC-BY-4.0

const  base58 =  require('bs58')
const nacl = require('tweetnacl')

/**
 * @public
 * Ed25519 keypair in base58 (as BigchainDB expects base58 keys)
 * @type {Object}
 * @param {Buffer} [seed] A seed that will be used as a key derivation function
 * @property {string} publicKey
 * @property {string} privateKey
 */
function Ed25519Keypair(seed) {
    const keyPair = seed ? nacl.sign.keyPair.fromSeed(seed) : nacl.sign.keyPair()
    this.publicKey = base58.encode(Buffer.from(keyPair.publicKey))
    // tweetnacl's generated secret key is the secret key + public key (resulting in a 64-byte buffer)
    this.privateKey = base58.encode(Buffer.from(keyPair.secretKey.slice(0, 32)))
}

module.exports = {
    Ed25519Keypair
}
