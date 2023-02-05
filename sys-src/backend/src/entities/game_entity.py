import random
import string
from typing import Dict, Optional, TypedDict

from mypy_boto3_dynamodb.service_resource import Table

from entities.base_entity import (
    Entity,
    EntityRepository,
    EntityService,
    RawEntity,
)
from entities.custom_types import USER_ENTITY_PREFIX, GameSide, GameStatus
from entities.game_user_relation import GameUserRelation, GameUserService
from entities.user_game_relation import UserGameRelation, UserGameService
from game_state import append_action_to_state
from utils import get_time


class GameInformation(TypedDict):
    State: str
    Status: int
    StartTime: int
    UpdateTime: int
    ASideConnections: Dict[str, str]
    BSideConnections: Dict[str, str]
    GuestConnections: Dict[str, str]


class RawGameEntity(RawEntity, GameInformation):
    pass


class GameEntity(Entity, GameInformation):
    GameId: str


class GameRepository(EntityRepository[RawGameEntity, GameEntity]):
    """
    Repository class for game entities with key schema:
        PK: Game_[GAME_ID]
        SK: Game_[GAME_ID]
    Entity primary key field name: GameId
    """

    def __init__(
        self,
        table: Table,
    ) -> None:
        super().__init__(
            table, prefix=USER_ENTITY_PREFIX, entity_pk_field="GameId"
        )


class GameService(EntityService[GameEntity]):
    def __init__(
        self,
        repository: GameRepository,
        user_game_service: UserGameService,
        game_user_service: GameUserService,
    ):
        super().__init__(repository)
        self._user_game_service = user_game_service
        self._game_user_service = game_user_service
        self._id_alphabet = string.ascii_letters + string.digits

    def create_new_game(
        self, game_id: Optional[str], username: str, user_connection_id: str
    ) -> GameEntity:
        if game_id is None:
            game_id = self._generate_game_id()

        if self.exists_by_key(game_id):
            raise Exception("Game item with id=%s already exists" % game_id)

        current_time = get_time()

        new_entity = GameEntity(
            GameId=game_id,
            State="",
            Status=GameStatus.STARTED.value,
            StartTime=current_time,
            UpdateTime=current_time,
            ASideConnections={username: user_connection_id},
            BSideConnections=dict(),
            GuestConnections=dict(),
        )
        self._repository.save(new_entity)

        user_game_relation = UserGameRelation(
            Username=username,
            GameId=game_id,
            GameStatus=GameStatus.STARTED.value,
            GameSide=GameSide.A.value,
            StartTime=current_time,
            JoinTime=current_time,
        )
        self._user_game_service.save(user_game_relation)

        game_user_relation = GameUserRelation(
            GameId=game_id, Username=username, JoinTime=current_time
        )
        self._game_user_service.save(game_user_relation)

        return new_entity

    def add_user_to_game_side(
        self,
        game_id: str,
        username: str,
        side: GameSide,
        user_connection_id: str,
    ) -> GameEntity:
        game_entity = self._get_non_null_by_key(game_id)
        current_time = get_time()

        game_entity["GuestConnections"].pop(username, "")
        if side == GameSide.A:
            game_entity["ASideConnections"][username] = user_connection_id
        else:
            game_entity["BSideConnections"][username] = user_connection_id
        self._repository.save(game_entity)

        user_game_relation = UserGameRelation(
            Username=username,
            GameId=game_id,
            GameStatus=GameStatus.STARTED.value,
            GameSide=side.value,
            StartTime=game_entity["StartTime"],
            JoinTime=current_time,
        )
        self._user_game_service.save(user_game_relation)

        game_user_relation = GameUserRelation(
            GameId=game_id, Username=username, JoinTime=current_time
        )
        self._game_user_service.save(game_user_relation)

        return game_entity

    def add_user_as_guest(
        self, game_id: str, username: str, user_connection_id: str
    ) -> GameEntity:
        game_entity = self._get_non_null_by_key(game_id)

        game_entity["GuestConnections"][username] = user_connection_id
        self._repository.save(game_entity)

        return game_entity

    def append_state_action_to_game(
        self, game_id: str, state_action: str
    ) -> GameEntity:
        game_entity = self._get_non_null_by_key(game_id)
        game_entity["State"] = append_action_to_state(
            game_entity["State"], state_action
        )

        self._repository.save(game_entity)
        return game_entity

    def _generate_game_id(self) -> str:
        """
        :return: a randomly generated game id string with 8 characters
        """
        return "".join(random.choices(self._id_alphabet, k=8))
