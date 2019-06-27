import dropbox 
from dropbox.files import WriteMode 
from dropbox.exceptions import ApiError, AuthError 

DEBUG = False

class DropboxUploader(object): 

    '''
        config dict must be like this:
        {
            "access_token" : token,
            "app_name" : name_of_app
        }
    '''

    def __init__(self, local_file_path, config): 
        super(DropboxUploader,self).__init__() 

        self.access_token = config["access_token"] 
        self.file_path = local_file_path
        self.app_name = config["app_name"] 

    def proced_upload(self): 
        self.get_access() 
        self.upload_file() 

    def read_file_data(self): 
        with open(self.file_path, 'rb') as f: 
            self.data = f.read() 

    def get_access(self): 
        if len(self.access_token) == 0: 
            raise ValueError("Invalid Access Token") 

        self.dbx = dropbox.Dropbox(self.access_token) 

        try: 
            self.dbx.users_get_current_account() 

        except AuthError as err: 
            raise ValueError("Invalid access token.") 

    def get_dropbox_path(self): 
        file_name = self.file_path.split("/") 
        path = "/" + file_name[-1] 

        if DEBUG :
            print(path)
            
        return path 

    def upload_file(self): 
        self.read_file_data() 
        dropbox_path = self.get_dropbox_path() 

        try: 

            self.dbx.files_upload(self.data, dropbox_path, mode=WriteMode('overwrite')) 
      
        except Exception as err: 
            raise ValueError("Error while uploading data into dropbox.") 

    def get_download_link(self):
        link_metadata = self.dbx.sharing_create_shared_link_with_settings(self.get_dropbox_path())
        status_link = str(link_metadata.url)
        download_link = status_link[0:-1] + '1'
        return download_link
    
    def run(self): 
        self.proced_upload()
        return self.get_download_link() 
