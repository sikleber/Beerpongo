import os
from typing import Any, Dict, Type, cast

import boto3
from mypy_boto3_apigatewaymanagementapi.client import (
    ApiGatewayManagementApiClient,
)
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from cognito import CognitoJwtAuthenticationService
from entities.game_entity import GameRepository, GameService
from entities.game_user_relation import GameUserRepository, GameUserService
from entities.user_game_relation import UserGameRepository, UserGameService
from websocket import WebsocketService


class InstanceManager:
    def __init__(self) -> None:
        self._initialized: Dict[Type, Any] = {}

    @property
    def _dynamodb_resource(self) -> DynamoDBServiceResource:
        return self._initialized.setdefault(
            DynamoDBServiceResource,
            cast(DynamoDBServiceResource, boto3.resource("dynamodb")),
        )

    @property
    def _dynamodb_table(self) -> Table:
        return self._initialized.setdefault(
            Table, self._dynamodb_resource.Table(os.environ["DB_TABLE"])
        )

    @property
    def _game_repository(self) -> GameRepository:
        return self._initialized.setdefault(
            GameRepository, GameRepository(table=self._dynamodb_table)
        )

    @property
    def _game_user_repository(self) -> GameUserRepository:
        return self._initialized.setdefault(
            GameUserRepository, GameUserRepository(table=self._dynamodb_table)
        )

    @property
    def _user_game_repository(self) -> UserGameRepository:
        return self._initialized.setdefault(
            UserGameRepository, UserGameRepository(table=self._dynamodb_table)
        )

    def _api_client(
        self, api_domain_name: str, api_stage: str
    ) -> ApiGatewayManagementApiClient:
        return self._initialized.setdefault(
            ApiGatewayManagementApiClient,
            boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=f'https://{api_domain_name}/{api_stage}',
            ),
        )

    @property
    def game_service(self) -> GameService:
        return self._initialized.setdefault(
            GameService,
            GameService(
                self._game_repository,
                self._user_game_service,
                self._game_user_service,
            ),
        )

    @property
    def _user_game_service(self) -> UserGameService:
        return self._initialized.setdefault(
            UserGameService, UserGameService(self._user_game_repository)
        )

    @property
    def _game_user_service(self) -> GameUserService:
        return self._initialized.setdefault(
            GameUserService, GameUserService(self._game_user_repository)
        )

    @property
    def cognito_jwt_authentication_service(
        self,
    ) -> CognitoJwtAuthenticationService:
        return self._initialized.setdefault(
            CognitoJwtAuthenticationService,
            CognitoJwtAuthenticationService(
                region=os.environ["AWS_REGION"],
                user_pool_id=os.environ["USER_POOL_ID"],
                app_client_id=os.environ["APP_CLIENT_ID"],
            ),
        )

    def websocket_service(
        self, api_domain_name: str, api_stage: str
    ) -> WebsocketService:
        return self._initialized.setdefault(
            WebsocketService,
            WebsocketService(self._api_client(api_domain_name, api_stage)),
        )


manager = InstanceManager()
