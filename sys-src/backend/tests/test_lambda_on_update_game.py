import json
from unittest.mock import ANY

from moto import mock_apigatewayv2, mock_dynamodb

from tests.resources import *
from websocket_lambdas.lambda_on_update_game import on_update_game


@mock_dynamodb
def test_on_update_game(dynamodb):
    games_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = games_table.name
    test_game_id = "GAME_ID"
    test_state = "TEST_STATE"
    test_connection_ids = ["1", "2", "3"]
    test_connection_id = "2"
    test_domain_name = "DOMAIN"
    test_stage = "STAGE"

    existing_item = {
        "GameId": test_game_id,
        "State": "INITIAL_STATE",
        "PlayerCount": 1,
        "ConnectionIds": test_connection_ids,
    }

    expected_item = {
        "GameId": test_game_id,
        "State": "INITIAL_STATE" + "," + test_state,
        "PlayerCount": 1,
        "ConnectionIds": test_connection_ids,
    }

    expected_response = {
        "GameId": test_game_id,
        "State": "INITIAL_STATE" + "," + test_state,
    }

    # creating test_item
    games_table.put_item(Item=existing_item)

    event = dict()
    event["body"] = json.dumps({"GameId": test_game_id, "State": test_state})
    event["requestContext"] = {
        "connectionId": test_connection_id,
        "domainName": test_domain_name,
        "stage": test_stage,
    }

    response = on_update_game(event, {})

    assert response == {"statusCode": 200, "body": ANY}

    body = json.loads(response["body"])
    assert body == expected_response

    # assert game item in dynamodb
    data = games_table.scan()
    assert data["Count"] == 1
    assert data["Items"][0] == expected_item
