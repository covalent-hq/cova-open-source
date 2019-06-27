# coding: utf-8

from .file_processing.encryption_utils import encrypt_json_data
from .file_processing.file_save_handler import FileSaveHandler
from .file_processing.file_io import read_data, read_routing_nodes_cred, read_json_config_file
from .secret_sharing.get_secrets import getSecrets
from .file_processing import public_encryprion
from .cova_file_uploader.Uploader import FileUploader
import os
import json
import requests
import binascii

DEFAULT_DO_LOCAL_PATH = os.getcwd()
DEBUG_MODE = True

class DataOwnerFileProcessor(object):
    """docstring for DataOwnerFileProcessor"""
    def __init__(self, file_path, policies, config_file_path = None):
        super(DataOwnerFileProcessor, self).__init__()
        """
            Initialize Global Variables

            Parameters
            ----------
            file_path : str
                Data Set file path
            
            policies : dictionary
                Policies of data set

            Returns
            -------
        """
        self.file_path = file_path 
        self.policies = policies
        self.data_hash = "" 
        self.config_file_path = config_file_path

        if config_file_path == None: 
            self.config_file_path = "DOConfig.conf"

    def read_file(self):
        """ 
            Read file data from given file path. Data is saved in self.data 

            Parameters
            ----------
            

            Returns
            -------
            True
                if read file is successful

            String
                if there is problem in file reading error will be returned
        """

        try:
            self.data = read_data(self.file_path)
            print("Dataset loaded Successfully")
        except:
            print("Error while loading Dataset")
            raise ValueError("Invalid File Path")

    def generate_policies(self):
        """ 
            Convert policies into json format. Save it into self.policy_json

            Parameters
            ----------
            

            Returns
            -------
            True
                if conversion is successful

            String
                if there is problem in generating policies
        """

        try:
            if (type(self.policies) is dict) == False:
                raise ValueError("Policies is not Dict")

            self.policy_json = json.dumps(self.policies)
            print("Smart Policy Generated Successfully")
        except:
            print("Error while generating smart policy")
            raise ValueError("Error in converting Json")

    def create_smart_data(self):
        """ 
            Create smart data by combining data and policy. self.smart_data  format is json.


            Parameters
            ----------
            

            Returns
            -------
            True
                if smart_data is created successfully

            String
                if error is occured in creating smart_data
        """

        try:
            temp_data = {"data": self.data.decode("utf-8") , "policies": self.policy_json}
            self.smart_data = json.dumps(temp_data)
            print("Smart Data Created Successfully")
        except:
            print("Error while generating smart data")
            raise ValueError("Error in Data or Policy or Both")

    def encrypt_smart_data(self):
        """ 
            This method encrypt smart_data. self.secrets and self.enc_data will contain secret key and encrypted data accordingly.

            Parameters
            ----------
            

            Returns
            -------
            True
                if data is encrypted successfully

            String
                Error in encrypting data
        """
        try:
            self.enc_data, self.secrets = encrypt_json_data(self.smart_data)
            print("Smart Data Encrypted Successfully")
        except:
            print("Error while encrypting smart data")
            raise ValueError("Error in data encrypring")

    def save_encrypted_file(self):
        """ 
            Save encrypted data and key in data_hash.enc and data_hash_key.enc

            Parameters
            ----------
            

            Returns
            -------
            True
                if data is saved successfully

            String
                Error in saving data
        """
        try:
            fileSave = FileSaveHandler()
            self.data_hash = fileSave.save_file_with_secrets(self.enc_data, self.secrets, path=DEFAULT_DO_LOCAL_PATH)
            print("Encrypted Data saved successfully")
            print("Encrypted Data Hash: %s" % self.data_hash)
        except:
            print("Error while saving encrypted smart data")
            raise ValueError("Error Occured while file is saving") 

    def upload_file(self):
        """ 
            Upload file in server

            Parameters
            ----------
            

            Returns
            -------
            True
                if uploaded successfully

            String
                if there is problem while uploading
        """
        try:
            encrypted_file_path = DEFAULT_DO_LOCAL_PATH + "/" + self.data_hash + ".enc" 
            uploader = FileUploader(encrypted_file_path, self.config_file_path) 
            self.download_link = uploader.run()
            
            if DEBUG_MODE:
                print("Download link "+self.download_link)

            print("Successfully uploaded to cloud")

        except Exception as error:
            print("Error occured while uploading file in server")
            raise ValueError("Error occured while uploading file in server")

    def run(self):
        """ 
            Run data processing step by step

            Parameters
            ----------
            
            Returns
            -------
            
        """
        self.read_file()
        self.generate_policies()
        self.create_smart_data()
        self.encrypt_smart_data()
        self.save_encrypted_file()
        self.upload_file()

class DataOwnerSecretUploader(object):
    """docstring for DataOwnerSecretUploader"""
    def __init__(self, smart_data_hash, 
            eth_wallet_id, eth_private_key, bdb_pub,bdb_private, download_link, config_file_path = None, routing_node_config_file = None):
        super(DataOwnerSecretUploader, self).__init__()
        """ 
            Initialize Global Variables

            Parameters
            ----------
            smart_data_hash : str
                Hash of smart data

            eth_wallet_id : str
                Ethereum public key

            eth_private_key : str
                Ethereum private key

            bdb_pub : str
                BigchainDB public key

            bdb_private : str
                BigchainDB private key

            download_link : str
                Dataset download link

            Returns
            -------
        
        """
        self.smart_data_hash = smart_data_hash
        self.eth_wallet_id = eth_wallet_id
        self.eth_private_key = eth_private_key
        self.bdb_pub_key = bdb_pub 
        self.bdb_private_key = bdb_private
        self.download_link = download_link
        self.config_file_path = config_file_path 
        self.routing_node_config_file = routing_node_config_file

        if config_file_path == None: 
            self.config_file_path = "DOConfig.conf"

        if routing_node_config_file == None: 
            self.routing_node_config_file = "routing_nodes.txt"

        self.initialize_values()

    def initialize_values(self):
        """ 
            Initialize addresses and others from config file

            Parameters
            ----------

            Returns
            -------
        
        """
        keyPair = read_json_config_file(self.config_file_path)
        self.eth_address = keyPair["eth_address"]
        self.bdb_address = keyPair["bdb_address"]
        self.minNode = int(keyPair["minNode"])
        self.totalNode = int(keyPair["totalNode"])

    def read_data(self):
        """ 
            Read smart_data and secrets from DO_LOCAL_PATH using smart hash

            Parameters
            ----------

            Returns
            -------
            True
                if read file is successful

            String
                if there is problem in file reading error will be returned
        """
        try:
            self.smart_data = read_data(DEFAULT_DO_LOCAL_PATH + "/" + self.smart_data_hash + ".enc")
            self.secrets = read_data(DEFAULT_DO_LOCAL_PATH + "/" + self.smart_data_hash + "_key.enc")
            print("Encrypted data loaded successfully")
        except:
            print("Error while reading encrypted dataset")
            raise ValueError("Error while reading encrypted dataset")

    def data_register_into_blockchain(self):
        """ 
            Register dataset into blockchain

            Parameters
            ----------

            Returns
            -------
            True
                Dataset is registered successfully

            String
                if there is problem while registering data set
        """
        try:
            address = self.eth_address + "/payment/registerDataset" + "/" + str(self.smart_data_hash) + "/" + str(self.eth_private_key)
            req = requests.get(address,timeout=100)
            ret = json.loads(req.text) 
            if ret["error"] == False:
                return True

            print(ret)
            return ret["desc"]

        except Exception as err:
            if DEBUG_MODE: 
                print(err)
            return "Error while registering data into blockchain"
 
    def generate_secrets(self):
        """ 
            Generate secrets for routing node using shamir secret sharing

            Parameters
            ----------

            Returns
            -------
            True
                if secret is generated successfully

            String
                Error in generating secrets
        """
        try:
            hex_secrets = binascii.hexlify(self.secrets)
            
            if DEBUG_MODE == True :
                open("err.txt", "a").write(str(hex_secrets))
                open("err.txt", "a").write("\n")

            self.secrets_arr = getSecrets(hex_secrets, self.minNode, self.totalNode)
            print("Secrets generated successfully")
        except:
            print("Error in generating secrets")
            raise ValueError("Error in generating secrets")

    def upload_file_info_blockchain(self):
        """
            Upload dataset information into blockchain

            Parameters
            ----------

            Returns
            -------
            True
                if dataset is upload successfully

            String
                Error while uploading dataset
        """
        try: 
            pdata = dict()
            pdata["data_hash"] = self.smart_data_hash 
            pdata["data_link"] = self.download_link
            pdata["eth_address"] = self.eth_wallet_id

            routing_nodes = read_routing_nodes_cred(self.routing_node_config_file) 
            
            if self.totalNode != len(routing_nodes) :
                return "mismatch total node with founded routing nodes information"
            
            for i in range(len(routing_nodes)):
                node = routing_nodes["router"+str(i)]
                data = public_encryprion.encrypt_message(self.secrets_arr[i],node["rsa_public_key"])
                pdata["keyfrag_" + str(node["id"])] = str(data)

            pdata["bdb_public_key"] = self.bdb_pub_key
            pdata["bdb_private_key"] = self.bdb_private_key

            # print(pdata)

            if DEBUG_MODE == True:
                open("err.txt", "a").write(json.dumps(self.secrets_arr))
            
            url = self.bdb_address + "/register_dataset"
            temp = requests.post(url, data = pdata)
            ret = json.loads(temp.text)
            # print(ret)

            if(ret["success"] == True):
                print("File Info Uploaded into Blockchain Successfully")
                return
            
            raise ValueError(ret["description"])

        except Exception as e:

            if DEBUG_MODE == True:
                print("error",e)
            print("Error Occured while uploading info into blockchain")
            raise ValueError(e)

    def run(self):
        """ 
            Run dataset and secret upload step by step

            Parameters
            ----------
            
            Returns
            -------
            
        """
        self.read_data()
        # self.data_register_into_blockchain()
        self.generate_secrets()
        self.upload_file_info_blockchain()
        
        
