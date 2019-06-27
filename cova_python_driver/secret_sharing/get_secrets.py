from secretsharingng import secret_utility
import json

def getSecrets(data, minConsensusNode, totalNode):
    
    data_len = len(data)

    if data_len == 0:
        raise ValueError("No data exists for generating secrets")

    generator = secret_utility.SecretGenerator(data,minConsensusNode,totalNode)

    return generator.run()
