# coding: utf-8
import requests, random, json
from .file_processing.file_io import read_data, read_routing_nodes_cred, read_json_config_file
from .file_processing.public_encryprion import decrypt_message
from .cova_network_utils.network_utility import init_task, new_task
from covatls.client.cova_client_request import covatls 
import os

DEFAULT_DU_LOCAL_PATH = os.getcwd()

class DataUserCodeExecute(object):
    """docstring for DataUserCodeExecute"""
    def __init__(self, data_hash, timeout, eth_pub_key = None, eth_priv_key = None, code_file_path = None, config_file_path = None, routing_node_config_file = None):
        super(DataUserCodeExecute, self).__init__()
        """ 
            Initialize Global Variables

            Parameters
            ----------
            data_hash : str
                data_hash of selected data set
            
            eth_pub_key : str
                Ethereum public key

            eth_priv_key : str
                Ethereum private key

            timeout : int
                Code maximum runtime

            code_file_path : str
                Execution code file path

            Returns
            -------
        """
        self.data_hash = data_hash
        self.eth_pub_key = eth_pub_key
        self.eth_private_key = eth_priv_key
        self.timeout = timeout
        self.code_file_path = code_file_path
        self.task_id = None
        self.config_file_path = config_file_path
        self.routing_node_config_file = routing_node_config_file

        if code_file_path == None:
            self.code_file_path = "code.py"

        if config_file_path == None: 
            self.config_file_path = "DUConfig.conf" 

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
        try:
            keyPair = read_json_config_file(self.config_file_path) 
            
            self.eth_address = str(keyPair["eth_address"])
            self.totalNode = int(keyPair["total_routing_node"]) - 1
            self.bdb_address = str(keyPair["bdb_address"])
            self.bdb_public_key = str(keyPair["bdb_public_key"])
            self.bdb_private_key = str(keyPair["bdb_private_key"])
            self.public_key = str(keyPair["public_key"])
            self.private_key = str(keyPair["private_key"])
            self.eth_pub_key = str(keyPair["eth_pub_key"])
            self.eth_private_key = str(keyPair["eth_private_key"])
            print("All configs loaded successfully")
        except Exception as err:
            print("Error in user configs")
            raise err

    def find_dataset(self):
        """
            Find whether the dataset with the given hash exists in the blockchain.

            Parameters
            ----------

            Returns
            -------
            True/False
                Dataset status into blockchain

            String
                Error while quering dataset into blockchain
        """
        try:
            address = self.bdb_address + "/check_dataset" + "/" + str(self.data_hash)
            
            req = requests.get(address, timeout=10)
            ret = json.loads(req.text)

            assert ret["exists"] == True

            print("Given data hash is valid") 

        except:
            print("There is no matching data set with given data hash")
            raise ValueError("Error in finding dataset")
    
    def create_smart_contract(self, amount, routing_node_public_key, routing_node_eth_address):
        """ 
            Create smart contract on selected data_hash

            Parameters
            ----------
            amount : int
                cost of creating smart contract

            Returns
            -------
            True
                If smart is created successfully

            String
                Error while creating smart contract
        """
        try:
            address = self.eth_address + "/payment/getAddress"

            try:
                req = requests.get(address, timeout=10)
            except:
                print("Error while quering payment addresss")
                return
            
            tp = str(req.text)
            toAddress = tp
            # print(tp, toAddress, amount)
            # print("approve -> ", toAddress)
            address = self.eth_address + "/covacoin/approve/"  + str(self.eth_private_key) + "/" + str(toAddress) + "/" + str(amount)
            # print(address)
            try:
                req = requests.get(address, timeout=100)
            except:
                print("Error while approving coin ")
                raise ValueError("Error while approving coin !!")

            approve = json.loads(req.text)

            if approve["error"] == True:
                print("Internal error while approving")
                raise ValueError("Internal error while approving")

            print("Allowance approved in an Ethereum smart contract")
            print("Allowance Tx Id: " + str(approve["receipt"]["transactionHash"]))

            # print("transfer -> ", routing_node_eth_address)
            address = self.eth_address + "/payment/transferForTask/" + str(self.eth_private_key) + "/" + str(routing_node_eth_address) + "/"  + str(amount) + "/" + str(self.task_id) 
            # print(address)
            try:
                req = requests.get(address, timeout=100)
            except:
                print("Error while transfering for task")
                return

            # print("---------------------------")
            # print("response ", req.text)
            self.transaction_id_moneyTransfer = json.loads(req.text)
            # print(self.transaction_id_moneyTransfer)
            
            if self.transaction_id_moneyTransfer["error"] == True:
                raise ValueError("Error while transfering coin !!")

            print("Payment successful")
            print("Transfer Tx id: " + str(self.transaction_id_moneyTransfer["receipt"]["transactionHash"]))

            aggrement_data = {}
            aggrement_data["bdb_public_key"] = self.bdb_public_key
            aggrement_data["bdb_private_key"] = self.bdb_private_key
            aggrement_data["routing_node_bdb_public_key"] = routing_node_public_key
            aggrement_data["task_id"] = self.task_id
            aggrement_data["data_hash"] = self.data_hash
            aggrement_data["from_eth_address"] = self.eth_pub_key
            aggrement_data["expected_time"] = self.timeout
            aggrement_data["cost"] = amount
            aggrement_data["eth_tx"] = str(self.transaction_id_moneyTransfer["receipt"]["transactionHash"])
            # print(aggrement_data)
            address = self.bdb_address + "/create_agreement" 
            try:
                req = requests.post(address, data=aggrement_data)
            except Exception as er:
                print("Error while creating agreement ", er)
                return
            
            self.transaction_id_aggrement = json.loads(req.text)
            
            if self.transaction_id_aggrement["success"] == False:
                raise ValueError("Error while creating agreement")

            print("Agreement created successfully")
            print("Agreement BDB Tx id: " + str(self.transaction_id_aggrement["transaction_id"]))
            return True
            
        except Exception as error:
            print("error while creating smart contract", error)
            raise ValueError("Error while connecting with blockchain")

    def provision_compute_node(self):
        """
            Ask routing node to provision a compute node with smart contract id
            It provisions the compute node for timeout, t seconds

            Parameters
            ----------

            Returns
            -------
            True
                If successfully

            String
                Error while provisioning compute node
        """
        try:
            self.read_file()
            # router_id = random.randint(0, self.totalNode)
            router_id = 0
            router_id = "router" + str(router_id)
            
            routing_nodes = read_routing_nodes_cred(self.routing_node_config_file)
            
            if len(routing_nodes) != self.totalNode+1 :
                raise ValueError("Routing nodes and total node must be equal")

            self.routing_node = "http://" + routing_nodes[router_id]["public_ip"]
            
            temp = init_task(self.routing_node,self.timeout,self.data_hash,self.code,self.public_key, self.eth_pub_key) 
            
            self.task_id = str(temp["task_id"])
            
            print("Task is initiated successfully ( Task Id:" + self.task_id +" ) and Estimated cost of computation is " + str(temp["cost"]))

            assert self.create_smart_contract(temp["cost"], str(routing_nodes[router_id]["bdb_public_key"]), str(routing_nodes[router_id]["eth_address"])) == True
            
            try:
                # print("Called new Task")
                temp = new_task(self.task_id, self.routing_node, self.transaction_id_aggrement["transaction_id"], self.eth_pub_key)
            except:
                print("Error while starting new task")
                raise ValueError("Error while starting new task")
            # print("compute node id: ", temp)
            if temp == 'None' :
                raise ValueError("Didn't get computer node")

            print("Job has been assigned to a compute node through routing nodes")

            return True
            
        except Exception as e:
            print("Error while trying to assign job")
            raise e

    def read_file(self):
        """
            Read code from code_file_path

            Parameters
            ----------

            Returns
            -------
            True
                If code is readed successfully

            String
                Error while reading code
        """
        try:
            self.code = read_data(self.code_file_path)
            return True
        except:
            raise ValueError("Invalid File Path")                                                                                                                      

    def get_computation_result(self):

        try:                                                                                                              
            address = self.bdb_address + "/find_task/" + str(self.transaction_id_aggrement["transaction_id"])
            
            try:
                json_response = requests.get(address, timeout=10)
            except:
                print("Error while accessing bdb")
                return

            dict_response = json.loads(json_response.text)
            # print(dict_response)
            if dict_response["success"] == False:
                print("Error Occured in Bigchain internally")
                return False,"Error Occured in Bigchain internally"

            if dict_response["finished"] == False:
                print("NotFound. Task has not finished yet")
                return False,"NotFound. Task has not finished yet"

            print("Task has been finished and trying to download result....")
            address = self.routing_node
            address += "/give_me_result/"
            address += self.task_id

            try:
                response = covatls().get(address)
            except:
                print("Error while collecting result")
                return

            encrypted_result = response
            # print("result ",encrypted_result)
            # decrypted_result = encrypted_result
            decrypted_result = decrypt_message(encrypted_result,self.private_key)
            # print(decrypted_result)
            save_path = str(DEFAULT_DU_LOCAL_PATH) + "/" + str(self.task_id) + ".out"
            open(save_path, "w+").write(decrypted_result)
            print("Result saved successfully as " + save_path)
            address = self.bdb_address + "/see_details/" + str(self.transaction_id_aggrement["transaction_id"])
            print("For details log " + address)
            return True, "Finished"
                
        except Exception as error:
            return False,error 

    def run(self):
        """ 
            do all necessary steps one by one

            Parameters
            ----------
            
            Returns
            -------
            
        """
        self.find_dataset()
        self.provision_compute_node()