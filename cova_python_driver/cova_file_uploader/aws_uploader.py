import boto3 
import os
import errno
from botocore.exceptions import ClientError, ParamValidationError

debug = False

class AWS3Uploader(object):

    '''
        config dict must be like this:
        {
            "access_key_id" : user access key id, 
            "access_key" : user access key, 
            "bucket_name" : bucket name, 
            "aws_path" : aws file path
        }
    ''' 

    def __init__(self, file_path, config): 
        super(AWS3Uploader, self).__init__() 

        self.access_key_id = config["access_key_id"] 
        self.access_key = config["access_key"] 
        self.bucket_name = config["bucket_name"] 
        self.file_path = file_path 
        self.file_path_after_upload = config['aws_path'] 
    
    def get_access(self):
        if len(self.access_key) == 0: 
            raise ValueError("Invalid Access Key")
        self.client = boto3.client('s3', aws_access_key_id=self.access_key_id, aws_secret_access_key=self.access_key)
        return self.client

    def create_bucket(self):
        try:
            self.client.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-west-1'})
        except Exception as e:
            print e

    def upload_file(self):
        try:
            self.client.upload_file(self.file_path, self.bucket_name, self.file_path_after_upload, ExtraArgs={'ACL': 'public-read'})
        except OSError as e:
            if (e.errno == 2): print "Error: No such file or directory"
            elif (e.errno == 13): print "Error: Permission denied"
            elif (e.errno == 27): print "Error: File too large"
            elif (e.errno == 36): print "Error: File name too long"
            elif (e.errno == 62): print "Error: Timer expired"
            else : print "Error: Unknown"
        except ClientError as e:
            print e
        except ParamValidationError as e:
            print e
        except Exception as e:
            print e

    def get_download_url(self):
        url = '%s/%s/%s' % (self.client.meta.endpoint_url, self.bucket_name, self.file_path)
        return url

    def run(self):
        self.get_access() 
        self.upload_file() 
        return self.get_download_url() 
