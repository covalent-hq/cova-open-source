from bigchaindb_driver import BigchainDB
import time
bdb_root_url = 'http://vps198264.vps.ovh.ca:9984'
bdb = BigchainDB(bdb_root_url)


asset = {
	'data': 'My Fucking Asset'
}

metadata = {
	'comment': 'Fuck You! BigchainDB python driver!'
}

from bigchaindb_driver.crypto import generate_keypair
alice, bob = generate_keypair(), generate_keypair()

prepared_creation_tx = bdb.transactions.prepare(operation='CREATE', signers=alice.public_key, asset=asset, metadata=metadata)
print(prepared_creation_tx)

fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx, private_keys=alice.private_key)
print(fulfilled_creation_tx)

sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)
print(sent_creation_tx)

