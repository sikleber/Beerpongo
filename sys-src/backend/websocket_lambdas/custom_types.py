from typing import List, TypedDict

from typing_extensions import Required


class WebsocketResponse(TypedDict, total=False):
    statusCode: Required[int]
    body: str


class GameEntity(TypedDict):
    GameId: str
    State: str
    PlayerCount: int
    ConnectionIds: List[str]
