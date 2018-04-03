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
    

  
        

OUTPUT_FILE_DIR            = "C:\\Users\\Alpoor.Reddy\\Documents\\DOD-ABACUS\\Finance\\reports\\"
LOCAL_AWS_DIR              = "C:\\Users\\Alpoor.Reddy\\.aws\\"

LOCAL_CREDENTIAL_ORIG_FILE = LOCAL_AWS_DIR + "credentials-ORIG-ABACUS"
LOCAL_CONFILG_ORIG_FILE    = LOCAL_AWS_DIR + "config-ORIG-ABACUS"

LOCAL_CREDENTIAL_FILE      = LOCAL_AWS_DIR + "credentials"
LOCAL_CONFILG_FILE         = LOCAL_AWS_DIR + "config"


exTractDate = datetime.datetime.now().strftime("%Y-%m-%d")
exTractDateTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

shutil.copyfile(LOCAL_CREDENTIAL_ORIG_FILE ,  LOCAL_CREDENTIAL_FILE)
shutil.copyfile(LOCAL_CONFILG_ORIG_FILE , LOCAL_CONFILG_FILE )  
mfa_TOTP = input("Enter the MFA(ABACUS) code: ")


mfa_SERIAL =  input("Enter the MFA(ABACUS) device ARN:(default:arn:aws-us-gov:iam::404299396556:mfa/areddy) ")
if mfa_SERIAL == '':
   mfa_SERIAL = 'arn:aws-us-gov:iam::404299396556:mfa/areddy'
   
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

print('aws_acct_id', '|','alias','|','vpc_id','|','ec2_instance_id','|','name','|','Description', '|', 'platform','|','region az zone', '|','instance_type','|','state')
ec2 = session.resource('ec2')
iam = session.client('iam')
try:
    paginator = iam.get_paginator('list_account_aliases')
    for response in paginator.paginate():
      alias = response['AccountAliases']
    aliasS = ''.join(map(str,alias))
    iam = session.resource('iam')
    account_id = iam.CurrentUser().arn.split(':')[4]
    instances = ec2.instances.all()
    for instance in instances:
         print(account_id,'|',aliasS,'|',  instance.vpc_id, '|',instance.id, '|', namedesc(instance.tags), '|', ec2_platform(instance.platform),'|',instance.placement['AvailabilityZone'],'|', instance.instance_type,'|',instance.state["Name"])
except Exception  as e:
     print('--error with account--->' + account_id)
     # print (e)      
     
     
     
OUTPUT_FILE_DIR            = "C:\\Users\\Alpoor.Reddy\\Documents\\DOD-ABACUS\\Finance\\reports\\"
LOCAL_AWS_DIR              = "C:\\Users\\Alpoor.Reddy\\.aws\\"

LOCAL_CREDENTIAL_ORIG_FILE = LOCAL_AWS_DIR + "credentials-ORIG-DOD"
LOCAL_CONFILG_ORIG_FILE    = LOCAL_AWS_DIR + "config-ORIG-DOD"

LOCAL_CREDENTIAL_FILE      = LOCAL_AWS_DIR + "credentials"
LOCAL_CONFILG_FILE         = LOCAL_AWS_DIR + "config"


exTractDate = datetime.datetime.now().strftime("%Y-%m-%d")
exTractDateTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

shutil.copyfile(LOCAL_CREDENTIAL_ORIG_FILE ,  LOCAL_CREDENTIAL_FILE)
shutil.copyfile(LOCAL_CONFILG_ORIG_FILE , LOCAL_CONFILG_FILE )  
mfa_TOTP = input("Enter the MFA(GDITDOD) code: ")


mfa_SERIAL =  input("Enter the MFA(GDITDOD) device ARN:(default:arn:aws-us-gov:iam::352951280886:mfa/areddy) ")
if mfa_SERIAL == '':
   mfa_SERIAL = 'arn:aws-us-gov:iam::352951280886:mfa/areddy'
   
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

print('aws_acct_id', '|','alias','|','vpc_id','|','ec2_instance_id','|','name','|','Description', '|', 'platform','|','region az zone', '|','instance_type','|','state')
ec2 = session.resource('ec2')
iam = session.client('iam')
try:
    paginator = iam.get_paginator('list_account_aliases')
    for response in paginator.paginate():
      alias = response['AccountAliases']
    aliasS = ''.join(map(str,alias))
    iam = session.resource('iam')
    account_id = iam.CurrentUser().arn.split(':')[4]
    instances = ec2.instances.all()
    for instance in instances:
         print(account_id,'|',aliasS,'|',  instance.vpc_id, '|',instance.id, '|', namedesc(instance.tags), '|', ec2_platform(instance.platform),'|',instance.placement['AvailabilityZone'],'|', instance.instance_type,'|',instance.state["Name"])
except Exception  as e:
     print('--error with account--->' + account_id)
     # print (e)        