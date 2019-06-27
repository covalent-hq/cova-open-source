# import sys, os
# sys.path.append('./covalent-secure-modes')

import boto3
import json
import datetime
import string
import random
import time

from server_consts import *

def change_credentials(iam_user):
    return True

def check_available_instance():
    # ping for number of running jobs in the instance
    return "url"

def spawn_ec2_instance():
    # boto3 spawn with start script

    # write to local storage
    pass


def check_and_spawn_instance():
    server_url = check_available_instance()

    if server_url is None:
        server_url = spawn_ec2_instance()

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def datetime_json_helper(o):
 if isinstance(o, datetime.datetime):
    return o.__str__()

def save_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, default=datetime_json_helper)

    return True

def ping_server(url):
    return res


def connect_to_service(service_name, aws_cred):
    boto3.setup_default_session(region_name='us-west-2')

    return boto3.client(service_name,
            aws_access_key_id=aws_cred["AccessKeyId"],
            aws_secret_access_key=aws_cred["SecretAccessKey"]
            )


def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ServerSpawner(object):
    """docstring for ServerSpawner"""
    def __init__(self, aws_initial_cred_filepath=None):
        super(ServerSpawner, self).__init__()
        self.aws_initial_cred_filepath = aws_initial_cred_filepath
        self.first_time = (aws_initial_cred_filepath is not None)

    def load_credentials(self):
        if self.first_time:
            self.aws_initial_cred = load_json(self.aws_initial_cred_filepath)
        else:
            self.aws_initial_cred = load_json(AWS_CRED_SEALED_PATH)

        print self.aws_initial_cred

        # self.aws_new_cred = self.aws_initial_cred
            

    def initial_security_cleanup(self):
        client = connect_to_service('iam', self.aws_initial_cred)

        # Optional: as the IAM user will have no console access
        # no need to change pass
        # TODO: SGX generated random string
        # new_pass = "new_pass_123"
        # response = client.change_password(
        #     OldPassword=self.aws_initial_cred["Password"],
        #     NewPassword=new_pass
        # )
        
        # self.aws_new_cred = {"Password": new_pass}

        # change access and secret keys
        self.aws_new_cred = client.create_access_key(UserName=self.aws_initial_cred["UserName"])["AccessKey"]

        print self.aws_new_cred

        # TODO: save those in sealed storage for use next time
        save_json(self.aws_new_cred, AWS_CRED_SEALED_PATH)

        # delete old key
        client.delete_access_key(UserName=self.aws_initial_cred["UserName"], 
            AccessKeyId=self.aws_initial_cred["AccessKeyId"])


    def is_server_running(self):
        url = self.aws_initial_cred.get("server_url")
        if url is None:
            return False

        # check if the server is alive
        try:
            res = ping_server(url)
            return res["running"]
        except Exception as e:
            return False

    def spawn_ec2_instance(self):
        # TODO: use ntpstat to synchronize time
        # for now use 10 sec sleep as a hack
        time.sleep(10)
        client = connect_to_service('ec2', self.aws_new_cred)

        if self.aws_initial_cred.get("key_name") is not None:
            # delete old pair
            response = client.delete_key_pair(KeyName=self.aws_initial_cred.get("key_name"))

        # create a new keypair
        rand_string = id_generator()
        response = client.create_key_pair(KeyName=rand_string)
        

        # save keypair
        self.aws_new_cred["ec2_priv_key"] = response["KeyMaterial"]
        self.aws_new_cred["key_name"] = response["KeyName"]

        save_json(self.aws_new_cred, AWS_CRED_SEALED_PATH)

        # spawn an intance as per spec with new keypair
        response = client.run_instances(ImageId='ami-7ddf8005',
            UserData=START_CMD,
            InstanceType='t2.micro',
            MinCount=1,
            KeyName=rand_string,
            MaxCount=1)

        self.aws_new_cred["PrivateIpAddresses"] = response["Instances"][0]["PrivateIpAddresses"]
        self.PrivateIpAddresses = self.aws_new_cred["PrivateIpAddresses"]

        save_json(self.aws_new_cred, AWS_CRED_SEALED_PATH)
        return True
    
    def get_server_url(self):
        return self.aws_new_cred["server_url"]

    def run(self):
        self.load_credentials()

        if not self.is_server_running():
            self.initial_security_cleanup()
            self.spawn_ec2_instance()

        return self.get_server_url()

if __name__ == '__main__':
    spawner = ServerSpawner(aws_initial_cred_filepath=None)
    spawner.run()




        