var driver = require('bigchaindb-driver')

function get_bdb_cred(){
    return new driver.Ed25519Keypair()
}

module.exports = {
    get_bdb_cred
}
