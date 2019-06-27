const keygen = require('./Ed25519Keypair')

function get_bdb_cred(){
    return new keygen.Ed25519Keypair()
}

module.exports = {
    get_bdb_cred
}
