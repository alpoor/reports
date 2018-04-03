import boto3
import datetime
import os
import shutil
import subprocess
import time
 
def ec2_platform(pf):
    if not bool(pf):
       return 'Linux'
    else:
       return 'Windows'

def namedesc(tag):
    str1 = ''
    Name = ''
    Description = ''
    for x in tag:
       if  x['Key'] == 'Name':
          Name = x['Value']
       if  x['Key'] == 'Description':
          Description = x['Value']
    return Name + '|' + Description
    

  
        

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
mfa_TOTP = input("Enter the MFA(USPS) code: ")


mfa_SERIAL =  input("Enter the MFA(USPS) device ARN:(default:arn:aws-us-gov:iam::445015072241:mfa/alpoor.reddy) ")
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

bucket = 'crsdeventdb-fra'
prefix = './CRSDEVENT/backupset/'  

s3client = session.client('s3')
result = s3client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
for o in result.get('CommonPrefixes'):
    print(o.get('Prefix'))
    
    
    
paginator = s3client.get_paginator('list_objects')
for result in paginator.paginate(Bucket='crsdeventdb-fra',Prefix='./CRSDEVENT/backupset/',Delimiter='/'):
    for prefix in result.get('CommonPrefixes'):
        print(str(bucket) , str(prefix.get('Prefix')))
    
s3 = session.resource('s3')
bucket = s3.Bucket('crsdeventdb-fra')
for obj in bucket.objects.all():
    print(obj.key)
    
s3 = session.resource('s3')
bucket = s3.Bucket('crsdeventdb-fra')
for obj in bucket.objects.filter(Prefix='./CRSDEVENT/backupset/'):
  ##  s3.Object(bucket.name, obj.key).delete()