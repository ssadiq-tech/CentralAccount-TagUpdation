import boto3
from config import central_resource_arn, Member_resource_arn, role_name, account_ids

# Tags to add/patch
tags_to_update = {
    'Environment': 'Production',
    'Owner': 'DevOps Team',
    'Project': 'CentralizedBackup'
}

# Central account session (with permissions to assume roles)
session = boto3.Session()

def assume_role(account_id, role_name):
    sts_client = session.client('sts')
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'

    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='OrganizationAccountAccessRole'
    )

    credentials = response['Credentials']

    # Return a new boto3 session with assumed role credentials
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

# 1️⃣ Tagging resources in Central Account
central_client = session.client('resourcegroupstaggingapi')

central_response = central_client.tag_resources(
    ResourceARNList=central_resource_arn,
    Tags=tags_to_update
)

print("✅ Central Account tagging response:", central_response)

# Loop over each account and perform actions
for account_id in account_ids:
    assumed_session = assume_role(account_id, role_name)
    client = assumed_session.client('resourcegroupstaggingapi')

    # Example: Upfate the tags in the assumed account
    response = client.tag_resources(
    ResourceARNList=Member_resource_arn,
    Tags=tags_to_update
    )

print("Tagging response:", response)
