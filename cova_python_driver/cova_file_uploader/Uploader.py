from ..file_processing.file_io import read_json_config_file
from .dropbox_uploader import DropboxUploader 
from .aws_uploader import AWS3Uploader 
from .ipfs_uploader import ipfs_uploader 

DEBUG = True

class FileUploader(object):
    def __init__(self, local_file_path, config_file_path): 
        super(FileUploader,self).__init__() 
        data = read_json_config_file(config_file_path) 
        self.upload_server = data["upload_server"] 
        self.configuration = data[self.upload_server + "_cred"] 
        self.local_file_path = local_file_path

    def process_upload(self):
        if self.upload_server == "Dropbox": 
            try:
                uploader = DropboxUploader(self.local_file_path, self.configuration)
                return uploader.run()

            except Exception as err:
                if DEBUG:
                    print(err)

                raise ValueError("Error in DropboxUploader") 
        
        if self.upload_server == "AWS": 
            try:
                uploader = AWS3Uploader(self.local_file_path, self.configuration) 
                return uploader.run() 

            except Exception as err: 
                if DEBUG: 
                    print(err) 

                raise ValueError("Error in AWS3Uploader") 

        if self.upload_server == "IPFS": 
            try: 
                uploader = ipfs_uploader(self.local_file_path, self.configuration) 
                return uploader.run() 

            except Exception as err: 
                if DEBUG: 
                    print(err) 

            raise ValueError("Error in IPFS Uploader") 


    def run(self): 
        try: 
            return self.process_upload() 

        except: 
            raise ValueError("Error in DropboxUploader") 

        