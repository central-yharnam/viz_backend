import boto3 # client that talks to minio
import threading
import io #for binary buffer that will hold downloaded data in memory
from botocore.client import Config #Config for connection
from botocore.exceptions import ClientError #Error for active connection
from botocore.exceptions import EndpointConnectionError # Error for inactive connection
import urllib3 # Used to hide 
import pretty
import boto3.session
import os

with open(os.environ['MI_ENDPOINT']) as f:
    entry = f.read()
endpoint = entry

with open(os.environ['MI_ACCESSKEY']) as f:
    entry = f.read()
access_key = entry

with open(os.environ['MI_SECRETACCESS']) as f:
    entry = f.read()
secret_access_key = entry


class Minio_Module:
    # Initalizes connection to minio server
    def __init__(self):
        print("#############################################\nMINIO INITIALIZED\n############################################")
        boto = boto3.session.Session()
        #boto3_client_lock = threading.Lock()
        #Supresses warnings, since boto does not like self signed certs
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        #with boto3_client_lock:
        #Connection module
        try:
            self.s3 = boto.resource('s3',  #type
                            endpoint_url=endpoint, #web address
                            aws_access_key_id=access_key, #access key
                            aws_secret_access_key=secret_access_key, #secret key
                            config=Config(signature_version='s3v4'), #config 
                                         region_name='us-east-1', #region, minio requires a region ( used for cloud aspect, just ignore, default is us-east-1)
                            verify=False)#allows connections to "unsecure" ( self signed) certs
        except:
            print("Minio module credentials needed")

    #function to insert into database   
    def insert(self,file,id):
        pretty.contact("IN MINIO INSERT METHOD --- CURRENTLY INSERTING " + file)
        try:
            self.s3.Bucket('visual-data').upload_file(file,id) #attempts to upload
        except ClientError:
            pretty.failure("File does not exist on your pc")  #message if file error
            return False
        except EndpointConnectionError:
            print(EndpointConnectionError)
            pretty.failure("Connection was not established") # message if connection error
            return False
        pretty.success(file + " uploaded")
        return True
            
    def retrieve(self,file,id):
        pretty.utility("Minio contacted >>>")
        try:
            self.s3.Bucket('visual-data').download_file(id,file) #attemps to download
        except ClientError:
            pretty.failure("File does not exist") #message if file error
            return False
        except EndpointConnectionError:
            pretty.failure("Connection was not established") #message if connection error
            return False
        pretty.success("Minio retrieval successful <<< ")
        return True

    '''def temp_retrieve(self, file, id):
        pretty.utility("Minio contacted >>>")
        try:
            self.s3.Bucket('visual-data').download_file(id,file) #attemps to download
        except ClientError:
            pretty.failure("File does not exist") #message if file error
            return False
        except EndpointConnectionError:
            pretty.failure("Connection was not established") #message if connection error
            return False
        pretty.success("Minio retrieval successful <<< ")
        return True'''


    def download_to_mem(self, iden):
        print("in method to download to memory")
        byte_buffer = io.BytesIO()
        try:
            self.s3.Bucket('visual-data').download_fileobj(iden, byte_buffer)
        except ClientError:
            print("File does not exist") #message if file error
            return False
        except EndpointConnectionError:
            print("Connection was not established") #message if connection error

        return byte_buffer

    def delete_all(self):


        allObj = self.s3.Bucket('visual-data').objects.all()
        for keys in allObj:
            print(keys)
            keys.delete()

    def delete_item(self, del_key):
        print("in delete item method")
        print(del_key)
        try:
            self.s3.Object('visual-data', del_key).delete()
        except ClientError:
            print("File does not exist") #message if file error
            return False

        return True
        '''b = self.s3.Bucket('visual-data')
        k = self.s3.Key(b)
        k.key = del_key
        b.delete_key(del_key)'''


    #check for a file's existence in minio
    def exist(self, ident):
        print("in exist method")
        try:
            self.s3.Object('visual-data', ident).load()
        except ClientError:
            print("File does not exist") #message if file error
            return False

        return True

#test = Minio_Module()
#test.delete_all()
#test.insert('./example.config', '12345')

#test.delete_all()

#test.exist('asdf')
#test.exist('5e656675d3a3f6d478588518-rq')
