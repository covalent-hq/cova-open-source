from bigchaindb_driver import BigchainDB
import time
import requests

bdb_root_url = 'http://vps198264.vps.ovh.ca:9984'
bdb = BigchainDB(bdb_root_url)


def linear_backoff_commit(times, txSigned):
	delay = .5
	while times:
		try:
			tx = bdb.transactions.send_commit(txSigned)
			return {
				'error': False,
				'id': tx.id
			}
		except Excection as e:
			time.sleep(delay)
			times = times - 1

	return {
		'error': True,
		'desc': 'Can\'t commmit'
	}


def exponential_backoff_commit(times, txSigned):
	delay = 1
	while times:
		try:
			tx = bdb.transactions.send_commit(txSigned)
			return {
				'error': False,
				'id': tx.id
			}
		except Excection as e:
			time.sleep(delay)
			times = 2 * times

	return {
		'error': True,
		'desc': 'Can\'t commmit'
	}

def mixed_backoff_commit(times, txSigned):
	res = linear_backoff_commit(times, txSigned)
	if res.error == True:
		res = exponential_backoff_commit(times, txSigned)
	return res


def get_signed_transaction_from_unspent_list(sender_keypair, recipient_public_key, list_unspent, amount, metadata = None):
	try:
		sum = 0
		list_inputs = [],
		list_outputs = []
		senders_share = 0
		asset_id = None
		for i in range(len(list_unspent)):
			tx = bdb.transactions.retrieve(list_unspent[i].transaction_id)	
			tx_amount = parseInt(tx['outputs'][list_unspent[i].output_index]['amount'])
			if i == 0:
	        	asset_id = {
	        		'id': tx['asset']['id']
	        	}

	        output = tx['outputs'][list_unspent[i].output_index]

	        list_inputs.append({
			    'fulfillment': output['condition']['details'],
			    'fulfills': {
			        'output_index': list_unspent[i].output_index,
			        'transaction_id': tx['id']
			    },
			    'owners_before': output['public_keys']
			})

	        sum += tx_amount

	        if sum >= amount:
	            senders_share = sum - amount
	            break
	        
	    if senders_share > 0:
            list_outputs.append((sender_keypair.publicKey, senders_share)
        
        list_outputs.append((recipient_public_key, amount))

        if metadata == None:
            bdb_metadata = {
                'desc': 'transfering ' + amount + ' from ' + sender_keypair.publicKey + ' to ' + recipient_public_key
            }
        else:
            bdb_metadata = metadata
  

        
    	prepared_transfer_tx = bdb.transactions.prepare(operation='TRANSFER', asset= asset_id, inputs=list_inputs, recipients=list_outputs, metadata=bdb_metadata)
    	fulfilled_transfer_tx = bdb.transactions.fulfill(prepared_transfer_tx, private_keys=sender_keypair.privateKey)
		
		else: 
			return	{
	    		'error': false,
	    		'signed_transaction': fulfilled_transfer_tx,
	    		'sum': sum
	   		}	

	except Excection as e:
		return {
			'error': true,
			'desc': e
		}


def transfer_tokens(sender_keypair, recipient_public_key, amount, metadata = null):
    signed_transaction
    try:
    	list_unspent = bdb.outputs.get(sender_keypair.publicKey, False)
    	signed_transaction_response = get_signed_transaction_from_unspent_list(sender_keypair, recipient_public_key, list_unspent, amount, metadata)
    	if signed_transaction_response.error == True:
    		return signed_transaction_response
        else:
        	signed_transaction = signed_transaction_response.signed_transaction
   	except Excection as e:
        return {
            'error': True,
            'status': e
        }

    if signed_transaction_response.sum < amount :
        return {
            'error': true,
            'status': "Not enought balance to transfer"
        }
    else:
        try:
        	tx =  mixed_backoff_commit(5, signed_transaction)
        	if tx.error == True:
        		return tx
     
            return {
                'error': False,
                'status': "Transfer successful",
                'transaction_id': tx['id']
            }
        except Excection as e:
            return {
                'error': True,
                'status': e
            }

def get_balance(user_public_key) {
    try:
        list_unspent = bdb.outputs.get(user_public_key, False)

        sum = 0

        for i in range(len(list_unspent)):
            tx = bdb.transactions.retrieve(list_unspent[i].transaction_id)	
	        tx_amount = parseInt(tx['outputs'][list_unspent[i]['output_index']]['amount'])
	        
            sum += tx_amount

        return {
            'error': False,
            'cova_balance': sum
        }
    
	except Exception as e:
        return {
            'error': True,
            'desc': e
        }
}


def get_unspent(user_public_key) {
    try:
        list_unspent = bdb.outputs.get(user_public_key, False)
        return {
            'error': False,
            'list_unspent': list_unspent
        }
    
	except Exception as e:
        return {
            'error': True,
            'desc': e
        }
}