# coding: utf-8

from file_processing.file_io import read_json_config_file
from data_owner import DataOwnerFileProcessor, DataOwnerSecretUploader 

DEBUG = False

class DataOwner(object): 
    def __init__(self, data_set_path, policies, upload_server = None, eth_pub = None, eth_private = None, bdb_pub = None, bdb_private = None):
        super(DataOwner, self).__init__()

        try:
            self.data_set_path = data_set_path 
            self.policies = policies 
            self.eth_pub = eth_pub 
            self.eth_private = eth_private 
            self.bdb_private = bdb_private 
            self.bdb_pub = bdb_pub 
            self.upload_server = upload_server
            self.data_hash = None 
            self.download_url = None 
            self.keyPair = read_json_config_file("DOConfig.conf")

            print("Data Owner Configs loaded successfully")
        except Exception as e:
            print("Error in Data Owner Configs")
            raise e


    def get_value(self, field_name):
        try:
            return self.keyPair[field_name]
        except:
            raise ValueError(str(field_name + " doesn't exist in dictionary."))

    def set_all_field(self):
        if self.eth_pub == None:
            self.eth_pub = self.get_value("eth_pub")

        if self.eth_private == None:
            self.eth_private = self.get_value("eth_private")

        if self.bdb_pub == None: 
            self.bdb_pub = self.get_value("bdb_pub") 

        if self.bdb_private == None:
            self.bdb_private = self.get_value("bdb_private")

        if self.upload_server == None: 
            self.upload_server = self.get_value("upload_server")

    def process_file(self): 
        FileProcessor = DataOwnerFileProcessor(self.data_set_path, self.policies)
        FileProcessor.run() 
        self.data_hash = FileProcessor.data_hash 
        self.download_url = FileProcessor.download_link 

    def process_uploads(self): 
        SecretUploader = DataOwnerSecretUploader(self.data_hash, self.eth_pub, self.eth_private, self.bdb_pub, self.bdb_private, self.download_url)
        SecretUploader.run()

    def run(self):
        self.set_all_field()
        self.process_file()
        self.process_uploads()
