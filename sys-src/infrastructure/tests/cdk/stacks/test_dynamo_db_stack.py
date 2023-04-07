import pytest
from aws_cdk.assertions import Template
from stacks.dynamo_db_stack import BeerpongoDynamoDbStack


@pytest.fixture
def dynamodb_stack(app, mock_config):
    yield BeerpongoDynamoDbStack(
        app,
        construct_id="BeerpongoDynamoDbStack",
        config=mock_config["dynamodbStack"],
    )


@pytest.fixture
def template(dynamodb_stack):
    yield Template.from_stack(dynamodb_stack)


def test_beerpongo_dynamo_db_table(template: Template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "BillingMode": "PAY_PER_REQUEST",
            "TableName": "BeerpongoTestTable",
            "AttributeDefinitions": [
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            "KeySchema": [
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
        },
    )


def test_beerpongo_dynamo_db_table_gsi(template: Template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "GSI_INDEX",
                    "KeySchema": [
                        {"AttributeName": "SK", "KeyType": "HASH"},
                        {"AttributeName": "PK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ]
        },
    )