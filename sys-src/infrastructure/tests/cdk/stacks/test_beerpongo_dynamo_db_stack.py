import pytest
from aws_cdk.assertions import Template
from stacks.beerpongo_dynamo_db_stack import BeerpongoDynamoDbStack


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


def test_beerpongo_dynamo_db_games_table(template: Template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "BillingMode": "PAY_PER_REQUEST",
            "TableName": "BeerpongoTestGamesTable",
            "AttributeDefinitions": [
                {"AttributeName": "GameId", "AttributeType": "S"},
            ],
            "KeySchema": [
                {"AttributeName": "GameId", "KeyType": "HASH"},
            ],
        },
    )
