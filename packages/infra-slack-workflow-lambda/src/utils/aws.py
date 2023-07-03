import os

import boto3

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
