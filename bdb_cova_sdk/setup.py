persistent_peers = '''persistent_peers = "936c28071b87ddcb8e06cdb2e194944e0136b8d3@vps198264.vps.ovh.ca:46656,\\
4ec9066a3602d4dc8bd4d269271751dd34b5600d@vps198265.vps.ovh.ca:46656,\\
6f8d5d6c2c75178418cc8e33c71342fbeba2dcc9@vps198266.vps.ovh.ca:46656,\\
1432485dfa4483f4363b07d62873199a584f73d6@vps198267.vps.ovh.ca:46656"
'''

print(persistent_peers)
yn = input("Looks good? (Y/N)")

if yn != 'Y':
    exit()


print("Opening config.toml")
with open(".tendermint/config/config.toml", "r") as f:
    txt = f.read()
    txt = txt.replace("create_empty_blocks = true", "create_empty_blocks = false")
    txt = txt.replace('persistent_peers = ""', persistent_peers)

    print(txt)

    print("rewriting config.toml")
    with open("./config.toml", "w") as f2:
        f2.write(txt)

print("This file changed")

