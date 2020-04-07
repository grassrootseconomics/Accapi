import os
import boto3
import json

secrets_client = boto3.client('secretsmanager')
secret_arn = 'arn:aws:secretsmanager:eu-central-1:847108109661:secret:/prod/dbcredentials-OEPfTY'
auth_token = secrets_client.get_secret_value(SecretId=secret_arn).get('SecretString')

d = json.loads(auth_token)
os.putenv('RDS_PASSWORD',d['password'])

print(d)
