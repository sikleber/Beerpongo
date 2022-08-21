import json
from unittest.mock import ANY

from moto import mock_dynamodb

from tests.resources import *
from websocket_lambdas.lambda_on_create_game import on_create_game


@mock_dynamodb
def test_on_create_game(dynamodb):
    games_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = games_table.name

    test_game_id = "GAME_ID"
    test_connection_id = "TEST_CONNECTION_ID"
    event = dict()
    event["body"] = json.dumps({"GameId": test_game_id})
    event["requestContext"] = {"connectionId": test_connection_id}

    response = on_create_game(event, {})

    # assert response
    assert response == {"statusCode": 200, "body": ANY}

    body = json.loads(response["body"])
    assert len(body) == 1
    assert body["GameId"] == test_game_id

    # assert game item in dynamodb
    data = games_table.scan()
    assert data["Count"] == 1
    assert data["Items"][0] == {
        "GameId": test_game_id,
        "State": "",
        "PlayerCount": 1,
        "ConnectionIds": ["TEST_CONNECTION_ID"],
    }


@mock_dynamodb
def test_on_create_existing_game_id_fails(dynamodb):
    games_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = games_table.name

    # put existing item
    existing_game_id = "GAME_ID"
    existing_item = {"GameId": existing_game_id, "State": "EXISTING_STATE"}
    games_table.put_item(Item=existing_item)

    test_connection_id = "TEST_CONNECTION_ID"
    event = dict()
    event["body"] = json.dumps({"GameId": existing_game_id})
    event["requestContext"] = {"connectionId": test_connection_id}

    response = on_create_game(event, {})

    # assert response
    assert response == {"statusCode": 500}

    # assert existing game item in dynamodb
    data = games_table.scan()
    assert data["Count"] == 1
    assert data["Items"][0] == existing_item
