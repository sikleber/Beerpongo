import json
import os
from unittest.mock import ANY

from moto import mock_dynamodb

from tests.resources import create_games_table
from websocket_handler import on_create_game, on_join_game, on_update_game


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
