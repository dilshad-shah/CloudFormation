import os

import boto3
import time

table_name = os.environ["DB_TABLE"]


def get_ssm_param(ssm_param_path):
    """Retrieve params from SSM."""
    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION"))
    resp = ssm.get_parameter(Name=ssm_param_path, WithDecryption=True)
    return resp["Parameter"]["Value"]


def put_dynamodb_item(json_payload):
    """pushes thread_ts <--> ticket_number into dynamodb"""
    db_client = boto3.client("dynamodb", region_name=os.environ.get("AWS_REGION"))
    return db_client.put_item(TableName=table_name, Item=json_payload)


def get_dynamodb_item(json_payload):
    """retrieves ticket_number for specific thread_ts provided"""
    db_client = boto3.client("dynamodb", region_name=os.environ.get("AWS_REGION"))
    return db_client.get_item(TableName=table_name, Key=json_payload)

def delete_dynamodb_item(json_payload):
    """retrieves ticket_number for specific thread_ts provided"""
    db_client = boto3.client("dynamodb", region_name=os.environ.get("AWS_REGION"))
    return db_client.delete_item(TableName=table_name, Key=json_payload)

def scan_dynamodb_items(timestamp):
    db_client = boto3.client("dynamodb", region_name=os.environ.get("AWS_REGION"))
    now = time.time()
    time_to_compare = now - timestamp

    response = db_client.scan(TableName=table_name, FilterExpression=Attr('threadId').lt(time_to_compare))
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = db_client.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data