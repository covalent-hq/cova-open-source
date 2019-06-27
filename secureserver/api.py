import os
from flask import Flask, request, jsonify
import requests
import bdb

from bigchaindb_driver import BigchainDB

from server_spawner import ServerSpawner

app = Flask(__name__)

os.environ['COVA_CLAVE_PUB_KEY'] = 'DapKQPcQ2fmZfdrNx7nUPkE3FwXdrVCmAtXL4BJgPXz2'
os.environ['COVA_CLAVE_PRIV_KEY'] = '2sCcJDKPgpCFtV36qzNVxaNecSUnri4NXYk9RqGymqGU'

sgx_keypair = {
	'publicKey': os.environ.get('COVA_CLAVE_PUB_KEY'),
	'privateKey': os.environ.get('COVA_CLAVE_PRIV_KEY')
} 


@app.route('/remote_attest')
def remote_attest():
	try:
		if(request.headers['covalent_token'] and request.headers['covalent_token'] == os.environ.get('COVALENT_TOKEN')):
			return jsonify(
					error = False,
					cova_clave_id = 0,
					attestation_hash = os.environ.get('ATTESTATION_HASH'),
	      			code_measurement_hash = os.environ.get('CODE_MEASUREMENT_HASH')
				)
		else:
			return jsonify(
					error = True,
					desc = 'Forbidden'
				), 403
	except Exception as e:
		return jsonify(
					error = True,
					desc = e
				)

@app.route('/public_key')
def public_key():
	try:
		return jsonify(
				error = False,
				public_key = sgx_keypair['publicKey']
			)
	except Exception as e:
		return jsonify(
					error = True,
					desc = e
				)


@app.route('/get_balance')
def get_balance():
	try:
		balance = bdb.get_balance(sgx_keypair['publicKey'])
		return jsonify(
				error = False,
				cova_balance = balance.cova_balance
			)

	except Exception as e:
		return jsonify(
					error = True,
					desc = e
				)

# TODO: Spawn a server
# We will be porting this full part to python to run inside grpahene-sgx
def spawn_server():
	spawner = ServerSpawner()
    spawner.run()

    url = spawner.PrivateIpAddresses

	aws_addr = 'http://ec2-52-7-138-56.compute-1.amazonaws.com:8080' if url is None else url

	return {
		'server_url': aws_addr,
		'success': True
	}


def ping_success_status(smart_contract_id, cova_transaction_id, server_params, ping_addr):
	resp_body = {
		'transaction_id': cova_transaction_id,
        'smart_contract_id': smart_contract_id,
        'server_url': server_params.server_url, 
        'success': server_params.success
	}

	url = ping_addr + '/api/status/success_server_spawn'
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
        'covalent-token': os.environ.get('COVALENT_TOKEN')
	}
	r = requests.post(url, headers=headers)	
	return r.content

def spawn_server_and_ping(smart_contract_id, cova_transaction_id, mt_addr="http://marketplace-api.covalent.ai",
        do_addr="https://protocol2.covalent.ai"):
	server_params = spawn_server()
	#Send MT request to send model to CS2
	ping_status = ping_success_status(smart_contract_id, cova_transaction_id, server_params, mt_addr)
	# TODO: Send DO request to send key to CS2
    # ^similar
    # ping_success_status(smart_contract_id, cova_transaction_id, server_params, do_addr)
	


@app.route('/spawn_server/<smart_contract_id>/<cova_transaction_id>')
def spawn_server_api_call(smart_contract_id, cova_transaction_id):
    try:
        # TODO: Make sure that the smart contract is released via a cron job 
        # through a concensus of several SGX nodes
        spawn_server_and_ping(smart_contract_id, cova_transaction_id)
    except Exception as e:
        return jsonify(
				error = True,
				desc = e
			)


@app.route('/send_smart_contract/<smart_contract_id>/<cova_transaction_id>')
def send_smart_contract(smart_contract_id, cova_transaction_id):
    # TODO: refactor
    try:
        return jsonify(
				error = False,
				status = 'sgx recieved smartcontract with id ' + smart_contract_id,
				smart_contract_id = smart_contract_id,
            	transaction_id = cova_transaction_id
			)
    except Exception as e:
        return jsonify(
				error = True,
				desc = e
			)


def relese_smart_contract(smart_contract_id, success):
	try:
		list_unspent_response = bdb.outputs.get(sgx_keypair['publicKey'], False)
		if list_unspent_response.error == True:
			return list_unspent_response
		else:
			list_unspent = list_unspent_response.list_unspent

	except Exception as e:
		return jsonify(
				error = True,
				desc = e
			)


	tx_of_interest = None
	for i in range(len(list_unspent)):
		if list_unspent[i].id == smart_contract_id:
			tx_of_interest = list_unspent[i]
		
	if tx_of_interest == None:
		return jsonify(
				error = True,
				desc = "Smart Contract ID is not valid / Smart Contract has been relased"
			)


	amount = tx_of_interest['outputs'][tx_of_interest['output_index']['amount']]
	list_inputs = []
	list_outputs = []
	asset_id = {
		'id': tx_of_interest['asset']['id']
	}
	send_to = tx_of_interest['metadata']['recipient']
	if success == 0:
		send_to = tx_of_interest['metadata']['sender']
	
	output = tx_of_interest['outputs'][tx_of_interest['output_index']]

	list_inputs.append({
		'fulfillment': output['condition']['details'],
		'fulfills': {
			'output_index': tx_of_interest['output_index'],
			'transaction_id': tx_of_interest['id']
		},
		'owners_before': output['public_keys']
	})

	list_outputs.append((send_to, amount))

	bdb_root_url = 'http://vps198264.vps.ovh.ca:9984'
	driver = BigchainDB(bdb_root_url)
	
	bdb_metadata = {
        'desc': 'transfering ' + amount + ' from ' + sgx_keypair['publicKey'] + ' to ' + send_to
    }

	prepared_transfer_tx = driver.transactions.prepare(operation='TRANSFER', asset= asset_id, inputs=list_inputs, recipients=list_outputs, metadata=bdb_metadata)
	fulfilled_transfer_tx = driver.transactions.fulfill(prepared_transfer_tx, private_keys=sgx_keypair['privateKey'])

	try:
		bdb_commit_response = bdb.mixed_backoff_commit(5, fulfilled_transfer_tx)
		return bdb_commit_response

	except Exception as e:
		return jsonify(
				error = True,
				desc = e
			)
		

if __name__ == '__main__':
	print(os.environ)
	app.run(host = '0.0.0.0', port = 3001)
	