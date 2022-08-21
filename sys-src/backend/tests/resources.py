import os

import boto3
import pytest

games_table_name = "TEST_GAMES_TABLE"


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"


@pytest.fixture
def dynamodb(aws_credentials):
    return boto3.resource("dynamodb")


def create_games_table(dynamodb):
    dynamodb.create_table(
        TableName=games_table_name,
        KeySchema=[
            {"KeyType": "HASH", "AttributeName": "GameId"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "GameId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    return dynamodb.Table(games_table_name)
