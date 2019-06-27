var driver = require('bigchaindb-driver')
var bip39 = require('bip39')
var crypto = require('crypto')
var request = require('async-request')
var md5 = require('md5')
var sleep = require('async-sleep')

const API_URL = 'http://vps198264.vps.ovh.ca:9984/api/v1/'

async function register_asset(asset, metadata, keypair){
	console.log(asset, keypair)
	const tx = driver.Transaction.makeCreateTransaction(
	    asset,
	    metadata,
	    [ driver.Transaction.makeOutput(driver.Transaction.makeEd25519Condition(keypair.publicKey)) ],
	    keypair.publicKey
	)

	const txSigned = driver.Transaction.signTransaction(tx, keypair.privateKey)
	const conn = new driver.Connection(API_URL)

	try{
		var retrievedTx = await conn.postTransactionCommit(txSigned)
		return {
			success: true,
			transaction_id: retrievedTx.id
		}	
	}
	catch(e){
		return {
			success: false,
			description: e
		}
	}
}

async function get_transaction_by_id(txID){
	try{
		const conn = new driver.Connection(API_URL)
		var tx = await conn.getTransaction(txID)
		return {
			success: true,
			transaction: tx
		}
	}
	catch(e){
		return {
			success: false,
			description: e
		}
	}
}

async function get_my_assets(user_public_key) {
    try {
		const conn = new driver.Connection(API_URL)
        list_unspent = await conn.listOutputs(user_public_key, 'false')
        return {
            success: true,
            list_unspent: list_unspent
        }
    } catch(e){
        return {
            success: false,
            desc: e
        }
    }
}

async function searchMetadatas(search_string){
	try{
		const conn = new driver.Connection(API_URL)
		var result = await conn.searchMetadata(search_string)
		return {
			success: true,
			result: result
		}
	}
	catch(e){
		return {
			success: false,
			description: e
		}
	}
}

async function searchAssets(search_string){
	try{
		const conn = new driver.Connection(API_URL)
		var result = await conn.searchAssets(search_string)
		return {
			success: true,
			result: result
		}
	}
	catch(e){
		return {
			success: false,
			description: e
		}
	}
}

module.exports = {
	register_asset,
	get_transaction_by_id,
	get_my_assets,
	searchMetadatas,
        searchAssets
}
