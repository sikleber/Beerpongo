import json
import os
from unittest.mock import ANY, Mock

import mock
from moto import mock_dynamodb

from entities.custom_types import GameStatus
from instance_manager import manager
from tests.resources import create_games_table
from utils import get_time
from websocket_handler import (
    CreateGameRequestBody,
    UpdateGameRequestBody,
    WebsocketEventAuthorizer,
    on_create_game,
    on_update_game,
)


@mock_dynamodb
def test_on_create_game(dynamodb):
    db_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = db_table.name
    game_service = manager.game_service

    test_game_id = "GAME_ID"
    test_username = "TEST_USER"
    test_connection_id = "TEST_CONNECTION_ID"
    event = dict()
    event_body = CreateGameRequestBody(GameId=test_game_id)
    event["body"] = json.dumps(event_body)
    event["requestContext"] = get_request_context(
        test_username, test_connection_id
    )

    min_time = get_time()
    response = on_create_game(event, {})
    max_time = get_time()

    # assert response
    assert response == {"statusCode": 200, "body": ANY}
    body = json.loads(response["body"])
    assert len(body) == 1
    assert body["GameId"] == test_game_id

    # assert game entity
    game_entity = game_service.get_by_key(test_game_id)
    assert game_entity["State"] == ''
    assert game_entity["Status"] == GameStatus.STARTED.value
    assert game_entity["StartTime"] >= min_time
    assert game_entity["StartTime"] <= max_time
    assert game_entity["UpdateTime"] >= min_time
    assert game_entity["UpdateTime"] <= max_time
    assert game_entity["ASideConnections"] == {
        test_username: test_connection_id
    }
    assert game_entity["BSideConnections"] == dict()
    assert game_entity["GuestConnections"] == dict()


@mock_dynamodb
def test_on_create_existing_game_id_fails(dynamodb):
    db_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = db_table.name
    game_service = manager.game_service

    test_game_id = "GAME_ID"
    existing_username = "TEST_USER"
    existing_connection_id = "TEST_CONNECTION_ID"

    # create existing game
    game_service.create_new_game(
        test_game_id, existing_username, existing_connection_id
    )

    event = dict()
    event["body"] = json.dumps({"GameId": test_game_id})
    event["requestContext"] = get_request_context("ANOTHER", "ANOTHER")
    response = on_create_game(event, {})

    # assert response
    assert response == {"statusCode": 500}

    # assert existing game entity
    game_entity = game_service.get_by_key(test_game_id)
    assert game_entity["ASideConnections"] == {
        existing_username: existing_connection_id
    }


@mock.patch("websocket_handler.manager")
@mock_dynamodb
def test_on_update_game(mock_manager, dynamodb):
    db_table = create_games_table(dynamodb)
    os.environ["DB_TABLE"] = db_table.name
    game_service = manager.game_service
    mock_manager.game_service = game_service
    mock_websocket = Mock()
    mock_manager.websocket_service = mock_websocket

    test_game_id = "GAME_ID"
    initial_username = "INITIAL_USER"
    initial_connection_id = "INITIAL_CONNECTION_ID"
    test_state_action = "STR_TO_ADD"

    # create initial game
    game_service.create_new_game(
        test_game_id, initial_username, initial_connection_id
    )

    event = dict()
    event_body = UpdateGameRequestBody(
        GameId=test_game_id, StateAction=test_state_action
    )
    event["body"] = json.dumps(event_body)
    event["requestContext"] = get_request_context("ANOTHER", "ANOTHER")
    response_data = on_update_game(event, {})

    assert response_data == {"statusCode": 200, "body": ANY}
    response = json.loads(response_data["body"])
    assert len(response) == 5
    assert response["GameId"] == test_game_id
    assert response["ASideUsers"] == [initial_username]
    assert response["BSideUsers"] == list()
    assert response["GuestUsers"] == list()
    assert response["State"] == test_state_action
    mock_websocket.callback_websocket_connections.assert_called_with(
        connection_ids=[initial_connection_id],
        callback_data=ANY,
    )


def get_request_context(username: str, connection_id: str) -> ANY:
    return {
        "connectionId": connection_id,
        "authorizer": WebsocketEventAuthorizer(
            username=username,
            email_verified=True,
            email="email",
            principalId=username,
        ),
    }
