import json
import os
from unittest.mock import ANY

import boto3
import pytest
from moto import mock_dynamodb

from rest_lambdas.post_lambda.lambda_post import post

table_name = 'test_table'


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-central-1'


@pytest.fixture
def dynamodb(aws_credentials):
    yield boto3.resource('dynamodb')


def create_games_table(dynamodb):
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'KeyType': 'HASH', 'AttributeName': 'GameId'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'GameId', 'AttributeType': 'S'},
        ],
        BillingMode='PAY_PER_REQUEST',
    )


@mock_dynamodb
def test_post(dynamodb):
    
    os.environ['DB_TABLE'] = table_name
    create_games_table(dynamodb)

    test_game_id = 'GAME_ID'
    event = {
        "TableName": table_name,
        "GameId": test_game_id
    }

    response = post(event, {})

    # assert response
    assert response == {"statusCode": 200, "body": ANY}

    body = json.loads(response["body"])
    assert len(body) == 3
    assert body["GameId"] == test_game_id
    assert body["State"] == ""
    assert body["PlayerCount"] == 1

    # assert game item in dynamodb
    data = dynamodb.Table(table_name).scan()
    assert data['Count'] == 1
    assert data['Items'][0] == {'GameId': test_game_id, 'State': '', "PlayerCount": 1}


@mock_dynamodb
def test_post_existing_game_id_fails(dynamodb):
    create_games_table(dynamodb)
    table = dynamodb.Table(table_name)

    # put existing item
    existing_game_id = 'GAME_ID'
    existing_item = {"GameId": existing_game_id, "State": "EXISTING_STATE"}
    table.put_item(Item=existing_item)

    event = {
        "GameId": existing_game_id
    }

    response = post(event, {})

    # assert response
    assert response == {"statusCode": 500}

    # assert existing game item in dynamodb
    data = table.scan()
    assert data['Count'] == 1
    assert data['Items'][0] == existing_item
