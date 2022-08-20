import json
from unittest.mock import ANY

from moto import mock_dynamodb

from tests.resources import *
from websocket_lambdas.lambda_on_join_game import on_join_game


@mock_dynamodb
def test_on_join_game(dynamodb):
    games_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = games_table.name
    test_game_id = "GAME_ID"
    existing_connection_id = "EXISTING_CONNECTION_ID"
    test_connection_id = "TEST_CONNECTION_ID"
    existing_item = {
        "GameId": test_game_id,
        "State": "",
        "PlayerCount": 1,
        "ConnectionIds": [existing_connection_id],
    }
    expected_item = {
        "GameId": test_game_id,
        "State": "",
        "PlayerCount": 2,
        "ConnectionIds": [existing_connection_id, test_connection_id],
    }
    expected_response = {
        "GameId": test_game_id,
        "State": "",
        "PlayerCount": "2",
    }

    # creating test_item
    games_table.put_item(Item=existing_item)

    event = dict()
    event["body"] = json.dumps({"GameId": test_game_id})
    event["requestContext"] = {"connectionId": test_connection_id}

    response = on_join_game(event, {})

    # assert response
    assert response == {"statusCode": 200, "body": ANY}

    body = json.loads(response["body"])
    assert body == expected_response

    # assert game item in dynamodb
    data = games_table.scan()
    assert data["Count"] == 1
    assert data["Items"][0] == expected_item


@mock_dynamodb
def test_on_join_game_not_found_fails(dynamodb):
    games_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = games_table.name
    test_game_id = "GAME_ID"
    test_connection_id = "TEST_CONNECTION_ID"

    event = dict()
    event["body"] = json.dumps({"GameId": test_game_id})
    event["requestContext"] = {"connectionId": test_connection_id}

    response = on_join_game(event, {})

    # assert response
    assert response == {"statusCode": 404}
