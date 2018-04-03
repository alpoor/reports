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



def sort_ids(infile , outfile):
        
        f  = open(infile , "r")
        fs = open(outfile , "w+")	
        lines = sorted(f.readlines())
        lines.sort()
        lines = [i.replace('\n' , '') for i in lines]
        for ln in lines:
           fs.write(ln)
           fs.write('\n')
        fs.close()
        f.close()

def uniq_ids(infile , outfile):
        
        d = {}
               
        
        text_file = open(infile ,  "r")
        fp = open(outfile , "w+")
        
        lines = text_file.readlines()
        for line in lines:
            if not line in d.keys():
                d[line] = 0
            d[line] = d[line]  +  1
 
        
        for line in lines:
            if d[line] == 0:
                continue
            elif d[line] == 2:
                fp.write(line)
                d[line] = 0
            else:
                fp.write(line)
        fp.close()
        
        
        
        

OUTPUT_FILE_DIR            = "C:\\Users\\Alpoor.Reddy\\Documents\\AWS CCS\\Finance\\reports\\"
LOCAL_AWS_DIR              = "C:\\Users\\Alpoor.Reddy\\.aws\\"

LOCAL_CREDENTIAL_ORIG_FILE = LOCAL_AWS_DIR + "credentials-ORIG"
LOCAL_CONFILG_ORIG_FILE    = LOCAL_AWS_DIR + "config-ORIG"

LOCAL_CREDENTIAL_FILE      = LOCAL_AWS_DIR + "credentials"
LOCAL_CONFILG_FILE         = LOCAL_AWS_DIR + "config"


exTractDate = datetime.datetime.now().strftime("%Y-%m-%d")
exTractDateTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

shutil.copyfile(LOCAL_CREDENTIAL_ORIG_FILE ,  LOCAL_CREDENTIAL_FILE)
shutil.copyfile(LOCAL_CONFILG_ORIG_FILE , LOCAL_CONFILG_FILE )  
mfa_TOTP = input("Enter the MFA code: ")


mfa_SERIAL =  input("Enter the MFA device ARN:(default:arn:aws:iam::175786337367:mfa/R10T) ")
if mfa_SERIAL == '':
   mfa_SERIAL = 'arn:aws:iam::175786337367:mfa/R10T'
   
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
        

iam = session.client('iam')



# Get the latest version - default versionID
response = iam.get_policy(PolicyArn='arn:aws:iam::175786337367:policy/aws-crossacct-assumerole-admin-policy')
PVersion = response['Policy']['DefaultVersionId']

# Get the Policy Statement details 
response1 = iam.get_policy_version(PolicyArn='arn:aws:iam::175786337367:policy/aws-crossacct-assumerole-admin-policy' , VersionId=PVersion)
PolicyStatmentiList = response1['PolicyVersion']['Document']['Statement']

if (len(PolicyStatmentiList))==1:
 PolicyStatment = PolicyStatmentiList[0]['Resource']

# Convert List item to String
PolicyStatment = ''.join(PolicyStatment)

awsIdList = ((PolicyStatment.replace(":role" , "\n")).replace("arn:aws:iam::" , "")).replace("/aws-crossacct-admin" , "")

aws_id_list_all_unsorted_fname = OUTPUT_FILE_DIR + "aws_id_list_all_unsorted_"  +  str(exTractDateTime)  +  ".txt"
f = open(aws_id_list_all_unsorted_fname  , "w+")

f.write(awsIdList)

response2 = iam.get_policy(PolicyArn='arn:aws:iam::175786337367:policy/aws-crossact-admin-policy-1')
PVersion1 = response2['Policy']['DefaultVersionId']

# Get the Policy Statement details
response3 = iam.get_policy_version(PolicyArn='arn:aws:iam::175786337367:policy/aws-crossact-admin-policy-1' , VersionId=PVersion1)
PolicyStatmentiList1 = response3['PolicyVersion']['Document']['Statement']

if (len(PolicyStatmentiList1))==1:
 PolicyStatment1 = PolicyStatmentiList1[0]['Resource']

# Convert List item to String
PolicyStatment1 = ''.join(PolicyStatment1)

awsIdList1 = ((PolicyStatment1.replace(":role" , "\n")).replace("arn:aws:iam::" , "")).replace("/aws-crossacct-admin" , "")
f.write(awsIdList1)
f.close()

aws_id_list_all_sorted_fname = OUTPUT_FILE_DIR + "aws_id_list_all_sorted_"  +  str(exTractDateTime)  +  ".txt"
aws_id_uniq_list_fname = OUTPUT_FILE_DIR + "aws_id_uniq_list_"  +  str(exTractDateTime)  +  ".txt"

sort_ids(aws_id_list_all_unsorted_fname , aws_id_list_all_sorted_fname)
uniq_ids(aws_id_list_all_sorted_fname , aws_id_uniq_list_fname)


infile = open(aws_id_uniq_list_fname , "r")


TEMP_CONFIG_FILE   = OUTPUT_FILE_DIR + "config" 
configFile = open(TEMP_CONFIG_FILE  , "w+")



configFile.write('[default]')
configFile.write('\n')
configFile.write('region = us-east-1')
configFile.write('\n')
configFile.write('\n')



for acct in infile:
    acct = acct.rstrip('\n')
    profile = '[profile '  +  str(acct)  +  ']'
    configFile.write(profile)
    configFile.write('\n')
    role_arn = 'role_arn = arn:aws:iam::'  +  str(acct)  +  ':role/aws-crossacct-admin'
    configFile.write(role_arn)
    configFile.write('\n')
    configFile.write('source_profile = default')
    configFile.write('\n')
    configFile.write('region = us-east-1')
    configFile.write('\n')
    configFile.write('\n')
configFile.close()
shutil.copyfile(TEMP_CONFIG_FILE ,  LOCAL_CONFILG_FILE)
infile.close()





aws_id_alias_list_fname = OUTPUT_FILE_DIR + "aws_id_alias_list_"  +  str(exTractDateTime)  +  ".txt"
aws_id_list_fname       = OUTPUT_FILE_DIR + "aws_id_list_"  +  str(exTractDateTime)  +  ".txt"
aws_id_error_list_fname = OUTPUT_FILE_DIR + "aws_id_error_list_"  +  str(exTractDateTime)  +  ".txt"

infile         = open(aws_id_uniq_list_fname , "r")
awsIDaliasFile = open(aws_id_alias_list_fname  , "w+")
awsIDnoerr     = open(aws_id_list_fname  , "w+")
awsIDerr       = open(aws_id_error_list_fname  , "w+")

header = str('aws_acct_id')  +  '|'  +  str('alias')
awsIDaliasFile.write(header)
awsIDaliasFile.write('\n')


start_time = time.localtime()

print(f"Generating aws alias file {aws_id_list_fname} at {time.strftime('%X',start_time)}... Please wait")

for acct in infile:
    acct = acct.rstrip('\n')
    session = boto3.session.Session(profile_name=acct)
    ec2 = session.resource('ec2')
    iam = session.client('iam')
    try:
        paginator = iam.get_paginator('list_account_aliases')
        for response in paginator.paginate():
            alias = response['AccountAliases']
        aliasS = ''.join(map(str , alias))
        record = str(acct)  +  '|'  +  str(aliasS)
        awsIDaliasFile.write(record)
        awsIDnoerr.write(acct)
        awsIDnoerr.write('\n')
        awsIDaliasFile.write('\n')
    except Exception  as e:
        record = str(acct)  +  '|'  +  str(e)
        awsIDerr.write(record)
        awsIDerr.write('\n')
        # print (e)

infile.close()
awsIDaliasFile.close()
awsIDnoerr.close()
awsIDerr.close()

stop_time = time.localtime()
difference = (time.mktime(stop_time) - time.mktime(start_time)) 
print(f"Generated aws alias file  {aws_id_list_fname} at {time.strftime('%X',stop_time)} in {difference} seconds... Please wait")


ec2_details_list_fname     = OUTPUT_FILE_DIR + "ec2_details_list_"  +  str(exTractDateTime)  +  ".csv"
ec2_details_list_err_fname = OUTPUT_FILE_DIR + "ec2_details_list_err_"  +  str(exTractDateTime)  +  ".csv"
ec2_count_details_fname    = OUTPUT_FILE_DIR + "ec2_count_details_"  +  str(exTractDateTime)  +  ".csv"

infile     = open(aws_id_list_fname , "r")
ec2file    = open(ec2_details_list_fname  , "w+")
ec2filerr  = open(ec2_details_list_err_fname  , "w+")
ec2filecnt = open(ec2_count_details_fname , 'w+')

header = 'aws_acct_id'  +  '|'  +  'alias'  +  '|'  +  'vpc_id'  +  '|'  +  'ec2_instance_id'  +  '|'  +  'platform'  +  '|'  +  'region az zone'  +  '|'  +  'instance_type'  +  '|'  +  'state'
header_cnt = 'aws_acct_id'  +  '|'  +  'alias'  +  '|'  +  'ec2_count'
ec2filecnt.write(header_cnt)
ec2filecnt.write('\n')
ec2file.write(header)
ec2file.write('\n')

print('\n')
print('\n')
start_time = time.localtime()
print(f"Generating EC2 details {ec2_details_list_fname} AND EC2 count {ec2_count_details_fname} at {time.strftime('%X',start_time)}... Please wait")


for acct in infile:
    acct = acct.rstrip('\n')
    session = boto3.session.Session(profile_name=acct)
    ec2 = session.resource('ec2')
    iam = session.client('iam')
    try:
        paginator = iam.get_paginator('list_account_aliases')
        for response in paginator.paginate():
            alias = response['AccountAliases']
        aliasS = ''.join(map(str , alias))
        instances = ec2.instances.all()
        instance_cnt = 0
        for instance in instances:
            record = str(acct)  +  '|'  +  str(aliasS)  +  '|'  +  str(instance.vpc_id)  +  '|'  +  str(instance.id)  +  '|'  +  str(ec2_platform(instance.platform))  +  '|'  +  str(instance.placement['AvailabilityZone'])  +  '|'  +  str(instance.instance_type)  +  '|'  +  str(instance.state["Name"])
            ec2file.write(record)
            ec2file.write('\n')
            instance_cnt = instance_cnt  +  1
       
        instance_cnt_record = str(acct)  +  '|'  +  str(aliasS)  +  '|'  +  str(instance_cnt)
        ec2filecnt.write(instance_cnt_record)
        ec2filecnt.write('\n')
        
           
                
    except Exception  as e:
        record = str(acct)  +  '|'  +  str(e)
        ec2filerr.write(record)
        ec2filerr.write('\n')
       
infile.close()
ec2file.close()
ec2filerr.close()
ec2filecnt.close()

stop_time = time.localtime()
difference = (time.mktime(stop_time) - time.mktime(start_time)) 
print(f"Generated EC2 details {ec2_details_list_fname} AND EC2 count {ec2_count_details_fname} at {time.strftime('%X',stop_time)} in {difference} seconds")


rds_details_list_fname     = OUTPUT_FILE_DIR + "rds_details_list_"  +  str(exTractDateTime)  +  ".csv"
rds_details_list_err_fname = OUTPUT_FILE_DIR + "rds_details_list_err_"  +  str(exTractDateTime)  +  ".csv"


infile     = open(aws_id_list_fname , "r")
rdsfile    = open(rds_details_list_fname  , "w+")
rdsfilerr  = open(rds_details_list_err_fname  , "w+")
 

start_time = time.localtime()
print('\n')
print('\n')
print(f"Generating RDS details file {rds_details_list_fname} at {time.strftime('%X',start_time)}... Please wait")


header = 'aws_acct_id' +  '|' + 'alias' + '|' + 'vpc_id' + '|' + 'InstanceId'  + '|' +  'SqlEngineType' + '|' + 'region az zone' +  '|' + 'instance_class' + '|' + 'Storage(GB)' +  '|' +  'MultiAZ' + '|'  +  'state'
rdsfile.write(header)
rdsfile.write('\n')

for acct in infile:
    acct = acct.rstrip('\n')
    session = boto3.session.Session(profile_name=acct)
    rds = session.client('rds')
    iam = session.client('iam')
    try:
        paginator = iam.get_paginator('list_account_aliases')
        for response in paginator.paginate():
            alias = response['AccountAliases']
        aliasS = ''.join(map(str , alias))
        response = rds.describe_db_instances()
        response1 = response['DBInstances']
        for instance in response1:
            instance1 = instance['DBSubnetGroup']
            vpc = instance1['VpcId']
            record = str(acct) +  '|'  +  str(aliasS)  +  '|'  +  str(vpc) +  '|'  + str(instance['DBInstanceIdentifier']) +  '|'  +   str(instance['Engine'])  +  '|'   +  str(instance['AvailabilityZone'])  +  '|'  +  str(instance['DBInstanceClass'])  +  '|'  +  str(instance['AllocatedStorage'])  +  '|'  +  str(instance['MultiAZ']) + '|' + str(instance['DBInstanceStatus'])
            rdsfile.write(record)
            rdsfile.write('\n')
    except Exception  as e:
       record = str(acct)  +  '|'  +  str(e)
       rdsfilerr.write(record)
       rdsfilerr.write('\n')

infile.close()
rdsfile.close()
rdsfilerr.close()

stop_time = time.localtime()
difference = (time.mktime(stop_time) - time.mktime(start_time)) 
print(f"Generated RDS details file {rds_details_list_fname} at {time.strftime('%X',stop_time)} in {difference} secconds")
 

redshift_details_list_fname     = OUTPUT_FILE_DIR + "redshift_details_list_"  +  str(exTractDateTime)  +  ".csv"
redshift_details_list_err_fname = OUTPUT_FILE_DIR + "redshift_details_list_err_"  +  str(exTractDateTime)  +  ".csv"


infile          = open(aws_id_list_fname , "r")
redshiftfile    = open(redshift_details_list_fname  , "w+")
redshiftfilerr  = open(redshift_details_list_err_fname  , "w+")
 
start_time = time.localtime()
print('\n')
print('\n')
print(f"Generating REDSHIFT details file {redshift_details_list_fname} at {time.strftime('%X',start_time)}... Please wait")
 

header = 'aws_acct_id' + '|' + 'alias' + '|' + 'vpc_id' + '|' + 'clusterId ' + '|' + 'Number of Nodes' + '|' + 'Node Type' + '|' + 'region/zone' + '|' + 'Status'
redshiftfile.write(header)
redshiftfile.write('\n')

 

for acct in infile:
    acct = acct.rstrip('\n')
    session = boto3.session.Session(profile_name=acct)
    try:
       iam = session.client('iam')
       paginator = iam.get_paginator('list_account_aliases')
       for response in paginator.paginate():
            alias = response['AccountAliases']
       aliasS = ''.join(map(str,alias))

       client =session.client('redshift')
       response = client.describe_clusters()
       response1 = response['Clusters'];
       for elem in response1:
            clsid    = elem['ClusterIdentifier']
            nodetype = elem['NodeType']
            azname   = elem['AvailabilityZone']
            clstatus = elem['ClusterStatus']
            nodecnt  = elem['NumberOfNodes']
            vpc = elem['VpcId']
            record = str(acct) + '|' + str(aliasS) + '|' + str(vpc) + '|' + str(clsid) + '|' + str(nodecnt) + '|' + str(nodetype) + '|' + str(azname) + '|' + str(clstatus) 
            redshiftfile.write(record)
            redshiftfile.write('\n')
    except Exception  as e:
            record = str(acct)  +  '|'  +  str(e)
            redshiftfilerr.write(record)
            redshiftfilerr.write('\n')
  
infile.close()
redshiftfile.close()
redshiftfilerr.close()

stop_time = time.localtime()
difference = (time.mktime(stop_time) - time.mktime(start_time)) 
print(f"Generated REDSHIFT details file {redshift_details_list_fname} at {time.strftime('%X',stop_time)} in {difference} seconds")





ebs_details_list_fname     = OUTPUT_FILE_DIR + "ebs_details_list_"  +  str(exTractDateTime)  +  ".csv"
ebs_details_list_err_fname = OUTPUT_FILE_DIR + "ebs_details_list_err_"  +  str(exTractDateTime)  +  ".csv"

infile          = open(aws_id_list_fname , "r")
ebsfile         = open(ebs_details_list_fname  , "w+")
ebsfilerr       = open(ebs_details_list_err_fname  , "w+")
 
start_time = time.localtime()
print('\n')
print('\n')
print(f"Generating EBS details file {ebs_details_list_fname} at {time.strftime('%X',start_time)}... Please wait")
 

header = 'aws_acct_id' + '|' +'alias' + '|' + 'volume_id' + '|' + 'volume_type' + '|' + 'Size(GiB)' + '|' + 'region az zone' + '|' + 'state'
ebsfile.write(header)
ebsfile.write('\n')


for acct in infile:
    acct = acct.rstrip('\n')
    session = boto3.session.Session(profile_name=acct)
    try:
       iam = session.client('iam')
       ec2 = session.resource('ec2')
       paginator = iam.get_paginator('list_account_aliases')
       for response in paginator.paginate():
            alias = response['AccountAliases']
       aliasS = ''.join(map(str,alias))

       volume_iterator = ec2.volumes.all()

       for volume in volume_iterator:
            record = str(acct) + '|' + str(aliasS) + '|' + str(volume.volume_id) + '|' + str(volume.volume_type) + '|' + str(volume.size) + '|' + str(volume.availability_zone) + '|' + str(volume.state)
            ebsfile.write(record)
            ebsfile.write('\n')
    except Exception  as e:
            record = str(acct)  +  '|'  +  str(e)
            ebsfilerr.write(record)
            ebsfilerr.write('\n')
  
infile.close()
ebsfile.close()
ebsfilerr.close()

stop_time = time.localtime()
difference = (time.mktime(stop_time) - time.mktime(start_time)) 
print(f"Generated EBS details file {ebs_details_list_fname} at {time.strftime('%X',stop_time)} in {difference} seconds")

