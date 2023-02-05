from typing import TypedDict

from mypy_boto3_dynamodb.service_resource import Table

from entities.base_relation import (
    RawRelation,
    Relation,
    RelationRepository,
    RelationService,
)
from entities.custom_types import GAME_ENTITY_PREFIX, USER_ENTITY_PREFIX


class UserGameInformation(TypedDict):
    GameStatus: int
    GameSide: int
    StartTime: int
    JoinTime: int


class RawUserGameRelation(RawRelation, UserGameInformation):
    pass


class UserGameRelation(Relation, UserGameInformation):
    Username: str
    GameId: str


class UserGameRepository(
    RelationRepository[RawUserGameRelation, UserGameRelation]
):
    """
    Repository class for user game entity relations with key schema:
        PK: User_[USERNAME]
        SK: Game_[GAME_ID]
    """

    def __init__(self, table: Table):
        super().__init__(
            table, USER_ENTITY_PREFIX, GAME_ENTITY_PREFIX, "Username", "GameId"
        )


class UserGameService(RelationService[UserGameRelation]):
    def __init__(self, repository: UserGameRepository):
        super().__init__(repository)
