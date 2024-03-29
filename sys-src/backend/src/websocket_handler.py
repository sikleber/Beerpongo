import json
import logging
import os
from typing import List, Optional, TypedDict, Union

from typing_extensions import Required

from cognito import AuthenticationResponse, CognitoJwtAuthenticationService
from entities.custom_types import EntityNotFoundException, GameSide
from entities.game_entity import GameEntity
from instance_manager import manager


class WebsocketEventAuthorizer(TypedDict):
    email_verified: bool
    principalId: str
    email: str
    username: str


class WebsocketRequestContext(TypedDict):
    domainName: str
    stage: str


class WebsocketResponse(TypedDict, total=False):
    statusCode: Required[int]
    body: str


class BaseGameBody(TypedDict):
    GameId: str


class CreateGameRequestBody(BaseGameBody, total=False):
    pass


class GuestJoinGameRequestBody(BaseGameBody):
    pass


class JoinGameRequestBody(BaseGameBody):
    GameSide: str


class UpdateGameRequestBody(BaseGameBody):
    StateAction: str


class CreateGameResponseBody(BaseGameBody):
    pass


class DefaultResponseBody(BaseGameBody):
    ASideUsers: List[str]
    BSideUsers: List[str]
    GuestUsers: List[str]
    State: str


def handler(
    event: dict, context: dict
) -> Union[AuthenticationResponse, WebsocketResponse]:
    handler_env = os.environ["HANDLER"]

    response: Union[
        AuthenticationResponse, WebsocketResponse
    ] = WebsocketResponse(statusCode=404)
    if handler_env == "AUTHENTICATE":
        response = on_authenticate(event)
    elif handler_env == "CONNECT":
        response = on_connect(event)
    elif handler_env == "CREATE_GAME":
        response = on_create_game(event)
    elif handler_env == "JOIN_GAME":
        response = on_join_game(event)
    elif handler_env == "JOIN_GAME_AS_GUEST":
        response = on_join_game_as_guest(event)
    elif handler_env == "UPDATE_GAME":
        response = on_update_game(event)
    else:
        logging.exception(
            "No handler found for lambda environment with HANDLER=%s",
            handler_env,
        )

    return response


def on_authenticate(event: dict) -> AuthenticationResponse:
    token = event["headers"]["Authorization"]
    auth_service: CognitoJwtAuthenticationService = (
        manager.cognito_jwt_authentication_service
    )

    return auth_service.authenticate(token, event["methodArn"])


def on_connect(event: dict) -> WebsocketResponse:
    try:
        authorizer: WebsocketEventAuthorizer = event["requestContext"][
            "authorizer"
        ]

        logging.info(f'Connected {authorizer["username"]}')
        logging.info(f'Event={event}')
    except Exception:
        logging.exception("Failed to log connection")

    return WebsocketResponse(statusCode=200)


def on_create_game(event: dict) -> WebsocketResponse:
    try:
        connection_id: str = event["requestContext"]["connectionId"]
        authorizer: WebsocketEventAuthorizer = event["requestContext"][
            "authorizer"
        ]
        body: CreateGameRequestBody = json.loads(event["body"])
        game_id: Optional[str] = body.get("GameId")

        game_service = manager.game_service
        new_game = game_service.create_new_game(
            game_id=game_id,
            user_connection_id=connection_id,
            username=authorizer["username"],
        )
        logging.debug("Created new game: %s", new_game)

        return WebsocketResponse(
            statusCode=200,
            body=json.dumps(CreateGameResponseBody(GameId=new_game["GameId"])),
        )
    except Exception:
        logging.exception("Failed to create new game")
        return WebsocketResponse(statusCode=500)


def on_join_game(event: dict) -> WebsocketResponse:
    try:
        body: JoinGameRequestBody = json.loads(event["body"])
        authorizer: WebsocketEventAuthorizer = event["requestContext"][
            "authorizer"
        ]
        connection_id: str = event["requestContext"]["connectionId"]
        game_id: Optional[str] = body.get("GameId")

        if game_id is None:
            raise Exception(
                "No game id specified in event body={0}".format(body)
            )

        game_side_str: Optional[str] = body.get("GameSide")
        if game_side_str == "A":
            game_side = GameSide.A
        elif game_side_str == "B":
            game_side = GameSide.B
        else:
            raise Exception(
                "Invalid game side specified in event body={0}".format(body)
            )

        service = manager.game_service
        game_entity = service.add_user_to_game_side(
            game_id=game_id,
            username=authorizer["username"],
            user_connection_id=connection_id,
            side=game_side,
        )

        return _process_changed_game_entity(
            game_entity, connection_id, event["requestContext"]
        )
    except EntityNotFoundException:
        logging.exception("No game found to join")
        return {"statusCode": 404}
    except Exception:
        logging.exception("Failed to join game")
        return WebsocketResponse(statusCode=500)


def on_join_game_as_guest(event: dict) -> WebsocketResponse:
    try:
        body: GuestJoinGameRequestBody = json.loads(event["body"])
        authorizer: WebsocketEventAuthorizer = event["requestContext"][
            "authorizer"
        ]
        connection_id: str = event["requestContext"]["connectionId"]
        game_id: Optional[str] = body.get("GameId")

        if game_id is None:
            raise Exception(
                "No game id specified in event body={0}".format(body)
            )

        service = manager.game_service
        game_entity = service.add_user_as_guest(
            game_id=game_id,
            username=authorizer["username"],
            user_connection_id=connection_id,
        )

        return _process_changed_game_entity(
            game_entity, connection_id, event["requestContext"]
        )
    except EntityNotFoundException:
        logging.exception("No game found to join")
        return {"statusCode": 404}
    except Exception:
        logging.exception("Failed to join game")
        return WebsocketResponse(statusCode=500)


def on_update_game(event: dict) -> WebsocketResponse:
    try:
        body: UpdateGameRequestBody = json.loads(event["body"])
        connection_id: str = event["requestContext"]["connectionId"]
        game_id = body.get("GameId")
        state_action = body.get("StateAction")
        if game_id is None:
            raise Exception("No game id specified in body={0}".format(body))
        elif state_action is None:
            raise Exception("No state specified in body={0}".format(body))

        service = manager.game_service
        game_entity = service.append_state_action_to_game(
            game_id, state_action
        )

        return _process_changed_game_entity(
            game_entity, connection_id, event["requestContext"]
        )
    except EntityNotFoundException:
        logging.exception("No game found to update")
        return WebsocketResponse(statusCode=404)
    except Exception:
        logging.exception("Failed to update game")
        return WebsocketResponse(statusCode=500)


def _process_changed_game_entity(
    game_entity: GameEntity,
    current_connection_id: str,
    request_context: WebsocketRequestContext,
) -> WebsocketResponse:
    response_data = _to_default_response(game_entity)
    _callback_game_users(
        game_entity=game_entity,
        current_connection_id=current_connection_id,
        data=response_data,
        api_domain_name=request_context["domainName"],
        api_stage=request_context["stage"],
    )

    return WebsocketResponse(statusCode=200, body=response_data)


def _callback_game_users(
    game_entity: GameEntity,
    current_connection_id: str,
    data: str,
    api_domain_name: str,
    api_stage: str,
) -> None:
    try:
        user_connections = game_entity["ASideConnections"]
        user_connections.update(game_entity["BSideConnections"])
        user_connections.update(game_entity["GuestConnections"])
        connection_ids = list(
            filter(
                lambda user_connection_id: user_connection_id
                != current_connection_id,
                list(user_connections.values()),
            )
        )

        service = manager.websocket_service(api_domain_name, api_stage)
        service.callback_websocket_connections(
            connection_ids=connection_ids,
            callback_data=data,
        )
    except Exception:
        logging.exception("Failed to callback game connections")


def _to_default_response(game_entity: GameEntity) -> str:
    response_body = DefaultResponseBody(
        GameId=game_entity["GameId"],
        State=game_entity["State"],
        ASideUsers=list(game_entity["ASideConnections"].keys()),
        BSideUsers=list(game_entity["BSideConnections"].keys()),
        GuestUsers=list(game_entity["GuestConnections"].keys()),
    )

    return json.dumps(response_body)
