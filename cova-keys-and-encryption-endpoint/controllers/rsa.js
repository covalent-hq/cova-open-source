var rsa = require('node-rsa')

function get_rsa_cred(){
    var keys = new rsa({b: 1024});

	return {
		publicKey: keys.exportKey('pkcs8-public'),
		privateKey: keys.exportKey('pkcs8')
	}
}

function rsa_encrypt(data, public_key){
    var imported_rsa_keys = new rsa()
    imported_rsa_keys.importKey(public_key, 'pkcs8-public')
    return imported_rsa_keys.encrypt(data, 'base64')
}

function rsa_decrypt(enc_data, private_key){
	var imported_rsa_keys = new rsa()
    imported_rsa_keys.importKey(private_key, 'pkcs8')
    return imported_rsa_keys.decrypt(enc_data, 'utf8')
}

module.exports = {
    get_rsa_cred,
    rsa_encrypt,
    rsa_decrypt
}