import random
import string
from typing import Any, List, Optional, TypedDict

import boto3


class GameEntity(TypedDict):
    GameId: str
    State: str
    PlayerCount: int
    ConnectionIds: List[str]


class EntityNotFoundException(Exception):
    """Raised when an expected entity could not be found"""

    pass


class GameRepository:
    def __init__(self, table_name: str) -> None:
        self._table: Any = boto3.resource("dynamodb").Table(table_name)

    def game_exists_by_id(self, game_id: str) -> bool:
        data = self._table.get_item(Key={"GameId": game_id})

        return "Item" in data

    def get_by_id(self, game_id: str) -> Optional[GameEntity]:
        data = self._table.get_item(Key={"GameId": game_id})

        return data.get("Item")

    def save(self, game_entity: GameEntity) -> None:
        self._table.put_item(Item=game_entity)


class GameService:
    def __init__(self, repository: GameRepository):
        self._repository = repository
        self._id_alphabet = string.ascii_letters + string.digits

    def game_exists_by_id(self, game_id: str) -> bool:
        return self._repository.game_exists_by_id(game_id)

    def get_by_id(self, game_id: str) -> Optional[GameEntity]:
        return self._repository.get_by_id(game_id)

    def create_new_game(
        self, initial_connection_id: str, game_id: Optional[str] = None
    ) -> GameEntity:
        if game_id is None:
            game_id = self._generate_game_id()

        if self.game_exists_by_id(game_id):
            raise Exception("Game item with id=%s already exists" % game_id)

        new_entity = GameEntity(
            GameId=game_id,
            State="",
            PlayerCount=1,
            ConnectionIds=[initial_connection_id],
        )

        self._repository.save(new_entity)
        return new_entity

    def add_player_connection_id_to_game(
        self, game_id: str, connection_id: str
    ) -> GameEntity:
        game_entity = self._get_non_null_by_id(game_id)
        game_entity["PlayerCount"] += 1
        game_entity["ConnectionIds"].append(connection_id)

        self._repository.save(game_entity)
        return game_entity

    def add_new_state_action_to_game(
        self, game_id: str, state_action: str
    ) -> GameEntity:
        game_entity = self._get_non_null_by_id(game_id)
        if len(game_entity["State"]) == 0:
            game_entity["State"] += state_action
        else:
            game_entity["State"] += "," + state_action

        self._repository.save(game_entity)
        return game_entity

    def _get_non_null_by_id(self, game_id: str) -> GameEntity:
        game_entity = self.get_by_id(game_id)
        if game_entity is None:
            raise EntityNotFoundException(
                "No item found for GameId={0}".format(game_id)
            )

        return game_entity

    def _generate_game_id(self) -> str:
        """
        :return: a randomly generated game id string with 8 characters
        """
        return "".join(random.choices(self._id_alphabet, k=8))
