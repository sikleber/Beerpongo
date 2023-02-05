from enum import Enum
from typing import Final

USER_ENTITY_PREFIX: Final[str] = "User_"
GAME_ENTITY_PREFIX: Final[str] = "Game_"


class GameSide(Enum):
    A = 0
    B = 1


class GameStatus(Enum):
    STARTED = 0
    CANCELED = 1
    FINISHED = 2


class EntityNotFoundException(Exception):
    """Raised when an expected entity could not be found"""

    pass
