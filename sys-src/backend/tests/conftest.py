import os

import boto3
import moto
import pytest
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

games_table_name = "TEST_GAMES_TABLE"


@pytest.fixture(scope="session")
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


@pytest.fixture(name="dynamodb_table")
def fixture_dynamodb_table(dynamodb: DynamoDBServiceResource):
    with moto.mock_dynamodb():
        table: Table = dynamodb.create_table(
            TableName=games_table_name,
            KeySchema=[
                {"KeyType": "HASH", "AttributeName": "PK"},
                {"KeyType": "RANGE", "AttributeName": "SK"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield dynamodb.Table(games_table_name)

