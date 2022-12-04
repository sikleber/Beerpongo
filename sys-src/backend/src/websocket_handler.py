import json
import logging
from typing import Optional, TypedDict

from typing_extensions import Required

from cognito import AuthenticationResponse, CognitoJwtAuthenticationService
from game_entity import EntityNotFoundException
from instance_manager import manager
from websocket_connection import callback_websocket_connections


class WebsocketResponse(TypedDict, total=False):
    statusCode: Required[int]
    body: str


class CreateGameBody(TypedDict, total=False):
    GameId: str


class CreateGameResponseBody(TypedDict):
    GameId: str


class JoinGameBody(TypedDict, total=False):
    GameId: str


class JoinGameResponseBody(TypedDict):
    GameId: str
    PlayerCount: str
    State: str


class UpdateGameBody(TypedDict, total=False):
    GameId: str
    State: str


class UpdateGameResponseBody(TypedDict):
    GameId: str
    State: str


def on_authenticate(event: dict, context: dict) -> AuthenticationResponse:
    token = event["headers"]["Authorization"]
    auth_service: CognitoJwtAuthenticationService = (
        manager.cognito_jwt_authentication_service
    )

    return auth_service.authenticate(token, event["methodArn"])


def on_connect(event: dict, context: dict) -> WebsocketResponse:
    return WebsocketResponse(statusCode=200)


def on_create_game(event: dict, context: dict) -> WebsocketResponse:
    try:
        connection_id: str = event["requestContext"]["connectionId"]
        body: CreateGameBody = json.loads(event["body"])
        game_id: Optional[str] = body.get("GameId")

        service = manager.game_service
        new_game = service.create_new_game(
            initial_connection_id=connection_id, game_id=game_id
        )
        logging.debug("Created new game: %s", new_game)

        return WebsocketResponse(
            statusCode=200,
            body=json.dumps(CreateGameResponseBody(GameId=new_game["GameId"])),
        )
    except Exception:
        logging.exception("Failed to create new game")
        return WebsocketResponse(statusCode=500)


def on_join_game(event: dict, context: dict) -> WebsocketResponse:
    try:
        body: JoinGameBody = json.loads(event["body"])
        connection_id: str = event["requestContext"]["connectionId"]
        game_id: Optional[str] = body.get("GameId")

        if game_id is None:
            raise Exception(
                "No game id specified in event body={0}".format(body)
            )

        service = manager.game_service
        game_entity = service.add_player_connection_id_to_game(
            game_id, connection_id
        )

        return WebsocketResponse(
            statusCode=200,
            body=json.dumps(
                JoinGameResponseBody(
                    GameId=game_id,
                    PlayerCount=str(game_entity["PlayerCount"]),
                    State=game_entity["State"],
                )
            ),
        )
    except EntityNotFoundException:
        logging.exception("No game found to join")
        return {"statusCode": 404}
    except Exception:
        logging.exception("Failed to join game")
        return WebsocketResponse(statusCode=500)


def on_update_game(event: dict, context: dict) -> WebsocketResponse:
    try:
        body: UpdateGameBody = json.loads(event["body"])
        current_connection_id: str = event["requestContext"]["connectionId"]
        game_id = body.get("GameId")
        state_action = body.get("State")
        if game_id is None:
            raise Exception("No game id specified in body={0}".format(body))
        elif state_action is None:
            raise Exception("No state specified in body={0}".format(body))

        service = manager.game_service
        game_entity = service.add_new_state_action_to_game(
            game_id, state_action
        )
    except EntityNotFoundException:
        logging.exception("No game found to update")
        return WebsocketResponse(statusCode=404)
    except Exception:
        logging.exception("Failed to update game")
        return WebsocketResponse(statusCode=500)

    response_body: UpdateGameResponseBody = UpdateGameResponseBody(
        GameId=game_id, State=game_entity["State"]
    )
    response_data = json.dumps(response_body)

    # callback game connections with new state
    try:
        connection_ids = list(
            filter(
                lambda connection_id: connection_id != current_connection_id,
                game_entity["ConnectionIds"],
            )
        )
        callback_websocket_connections(
            request_context=event["requestContext"],
            connection_ids=connection_ids,
            callback_data=response_data,
        )
    except Exception:
        logging.exception("Failed to callback game connections")

    return WebsocketResponse(statusCode=200, body=response_data)
