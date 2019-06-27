import requests
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import ipfsapi


class ipfs_uploader(object):
    '''
        {
            
        }
    '''
    def __init__(self, file_path, config):
        super(ipfs_uploader, self).__init__()

        self.file_path = file_path

    def get_access(self):
        self.api_client = ipfsapi.Client("https://ipfs.infura.io", 5001)

    def upload_file(self):
        self.item = self.api_client.add(self.file_path)

    def get_download_url(self):
        url = "https://ipfs.io/ipfs/" + self.item['Hash']
        return url

    def run(self):
        self.get_access()
        self.upload_file()
        return self.get_download_url()

if __name__ == '__main__':
    ipfs = ipfs_uploader("Uploader.py", {})
    print ipfs.run()