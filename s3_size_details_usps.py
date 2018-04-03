import boto3
import datetime
import os
import shutil
import subprocess
import time
     
  
        

OUTPUT_FILE_DIR            = "C:\\Users\\Alpoor.Reddy\\Documents\\AWS USPS CRS\\Finance\\reports\\"
LOCAL_AWS_DIR              = "C:\\Users\\Alpoor.Reddy\\.aws\\"

LOCAL_CREDENTIAL_ORIG_FILE = LOCAL_AWS_DIR + "credentials-ORIG-USPS"
LOCAL_CONFILG_ORIG_FILE    = LOCAL_AWS_DIR + "config-ORIG-USPS"

LOCAL_CREDENTIAL_FILE      = LOCAL_AWS_DIR + "credentials"
LOCAL_CONFILG_FILE         = LOCAL_AWS_DIR + "config"


exTractDate = datetime.datetime.now().strftime("%Y-%m-%d")
exTractDateTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

shutil.copyfile(LOCAL_CREDENTIAL_ORIG_FILE ,  LOCAL_CREDENTIAL_FILE)
shutil.copyfile(LOCAL_CONFILG_ORIG_FILE , LOCAL_CONFILG_FILE )  
mfa_TOTP = input("Enter the MFA code: ")


mfa_SERIAL =  input("Enter the MFA device ARN:(default:arn:aws-us-gov:iam::445015072241:mfa/alpoor.reddy) ")
if mfa_SERIAL == '':
   mfa_SERIAL = 'arn:aws-us-gov:iam::445015072241:mfa/alpoor.reddy'
   
client = boto3.client('sts')

response = client.get_session_token(
  DurationSeconds=900,
  SerialNumber=mfa_SERIAL, 
  TokenCode=mfa_TOTP
)
 
 
AWS_ACCESS_KEY_ID     = response['Credentials']['AccessKeyId']
AWS_SECRET_ACCESS_KEY = response['Credentials']['SecretAccessKey']
AWS_SESSION_TOKEN     = response['Credentials']['SessionToken']

TEMP_CREDENTIAL_FILE   = OUTPUT_FILE_DIR + "credentials" 

f = open(TEMP_CREDENTIAL_FILE  , "w+")
f.write('[default]')
f.write('\n')
f.write('AWS_ACCESS_KEY_ID='  +  AWS_ACCESS_KEY_ID)
f.write('\n')
f.write('AWS_SECRET_ACCESS_KEY='  +  AWS_SECRET_ACCESS_KEY)
f.write('\n')
f.write('AWS_SESSION_TOKEN='  +  AWS_SESSION_TOKEN)
f.close()

shutil.copyfile(LOCAL_CREDENTIAL_FILE,  LOCAL_CREDENTIAL_ORIG_FILE)
shutil.copyfile(TEMP_CREDENTIAL_FILE ,  LOCAL_CREDENTIAL_FILE)

session = boto3.Session(
           aws_access_key_id=response['Credentials']['AccessKeyId'],
           aws_secret_access_key=response['Credentials']['SecretAccessKey'], 
           aws_session_token=response['Credentials']['SessionToken']
        )
        

client = session.client('s3')
response = client.list_buckets()

s3 = session.resource('s3')

for bucket_name in response['Buckets']:
    bucket = s3.Bucket(bucket_name['Name'])        
    total_size = 0
    for k in bucket.objects.all():
       total_size += k.size
    print(bucket_name['Name'],'|' , str(total_size))
    
  

