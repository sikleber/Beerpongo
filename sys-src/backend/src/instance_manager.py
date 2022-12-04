import os
from typing import Any, Dict, Type

from cognito import CognitoJwtAuthenticationService
from game_entity import GameRepository, GameService


class InstanceManager:
    def __init__(self) -> None:
        self._initialized: Dict[Type, Any] = {}

    @property
    def _game_repository(self) -> GameRepository:
        return self._initialized.setdefault(
            GameRepository, GameRepository(table_name=os.environ["DB_TABLE"])
        )

    @property
    def game_service(self) -> GameService:
        return self._initialized.setdefault(
            GameService, GameService(self._game_repository)
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


manager = InstanceManager()
