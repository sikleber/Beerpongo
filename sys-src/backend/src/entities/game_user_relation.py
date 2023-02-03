from typing import TypedDict

from mypy_boto3_dynamodb.service_resource import Table

from entities.base_relation import (
    RawRelation,
    Relation,
    RelationRepository,
    RelationService,
)
from entities.custom_types import GAME_ENTITY_PREFIX, USER_ENTITY_PREFIX


class GameUserInformation(TypedDict):
    JoinTime: int


class RawGameUserRelation(RawRelation, GameUserInformation):
    pass


class GameUserRelation(Relation, GameUserInformation):
    GameId: str
    Username: str


class GameUserRepository(
    RelationRepository[RawGameUserRelation, GameUserRelation]
):
    """
    Repository class for user game entity relations with key schema:
        PK: Game_[GAME_ID]
        SK: User_[USERNAME]
    """

    def __init__(self, table: Table):
        super().__init__(
            table, GAME_ENTITY_PREFIX, USER_ENTITY_PREFIX, "GameId", "Username"
        )


class GameUserService(RelationService[GameUserRelation]):
    def __init__(self, repository: GameUserRepository):
        super().__init__(repository)
