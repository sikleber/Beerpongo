import os

import boto3
import pytest
from moto import mock_dynamodb

from rest_lambdas.get_lambda.lambda_get import get

table_name = "test_table"


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS credentials for moto"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"


@mock_dynamodb
def test_get_lambda(aws_credentials):
    # creating test_table

    os.environ['DB_TABLE'] = table_name
    dynamodb = boto3.client("dynamodb")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"KeyType": "HASH", "AttributeName": "GameId"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "GameId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # creating test_item
    dynamodb.put_item(
        Item={"GameId": {"S": "1"}, "State": {"S": "1:X,2:32"}},
        TableName=table_name,
    )

    # test if the right game state is returned
    event = {"params": {"path": {"GameId": "1"}}}
    resp = get(event, {})

    assert resp["statusCode"] == 200
    assert resp["body"]["State"] == "1:X,2:32"

    # test if the right error ist returned, if the gameID does not exist
    event = {"params": {"path": {"GameId": "a"}}}
    resp = get(event, {})

    assert resp["statusCode"] == 404
