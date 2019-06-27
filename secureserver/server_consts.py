import json

COVA_HEADER = {
      'content-type': 'application/x-www-form-urlencoded',
      'origin': 'secured-origin',
      'covalent-token': '*-d@}u%dy4p6A%JF?)$+DDO2DW4vO<'
    }

MT_API_URL = "https://marketplace-api.covalent.ai/api"


AWS_CRED_SEALED_PATH = "EC2_cred_sealed"

START_CMD = "curl -LOk  https://github.com/covalent-hq/covalent-secure-server/archive/master.tar.gz && tar  -xvf master.tar.gz && mv covalent-secure-server-master/* ./ && bash server_jobs.sh"