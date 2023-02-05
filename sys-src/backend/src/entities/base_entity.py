from abc import ABC
from typing import Any, Generic, Mapping, Optional, TypedDict, TypeVar, cast

from mypy_boto3_dynamodb.service_resource import Table

from entities.custom_types import EntityNotFoundException


class Entity(TypedDict):
    pass


class RawEntity(TypedDict):
    PK: str
    SK: str


TEntity = TypeVar("TEntity", bound=Entity)
TRawEntity = TypeVar("TRawEntity", bound=RawEntity)


class BaseRepository(ABC):
    def __init__(self, table: Table) -> None:
        self._table = table


class EntityRepository(BaseRepository, Generic[TRawEntity, TEntity], ABC):
    prefix: str
    entity_pk_field: str

    def __init__(
        self, table: Table, prefix: str, entity_pk_field: str
    ) -> None:
        super().__init__(table)
        self.prefix = prefix
        self.entity_pk_field = entity_pk_field

    def entity_exists_by_key(self, key: str) -> bool:
        data = self._table.get_item(
            Key={"PK": self.prefix + key, "SK": self.prefix + key}
        )

        return "Item" in data

    def get_by_key(self, key: str) -> Optional[TEntity]:
        data = self._table.get_item(
            Key={"PK": self.prefix + key, "SK": self.prefix + key}
        )

        if "Item" in data:
            raw_entity = cast(TRawEntity, data["Item"])
            return self.convert_raw(raw_entity)
        return None

    def save(self, entity: TEntity) -> None:
        raw_entity = self.convert_to_raw(entity)
        self._table.put_item(Item=cast(Mapping[str, str], raw_entity))

    def convert_raw(self, raw_entity: TRawEntity) -> TEntity:
        entity = dict()
        entity[self.entity_pk_field] = raw_entity["PK"].replace(
            self.prefix, ''
        )
        for key in raw_entity:
            if key != "PK" and key != "SK":
                entity[key] = cast(Any, raw_entity)[key]

        return cast(TEntity, entity)

    def convert_to_raw(self, entity: TEntity) -> TRawEntity:
        raw_entity: RawEntity = RawEntity(
            PK=self.prefix + cast(Any, entity)[self.entity_pk_field],
            SK=self.prefix + cast(Any, entity)[self.entity_pk_field],
        )
        for key in entity:
            if key != self.entity_pk_field:
                cast(Any, raw_entity)[key] = cast(Any, entity)[key]

        return cast(TRawEntity, raw_entity)


class EntityService(Generic[TEntity], ABC):
    def __init__(self, repository: EntityRepository[Any, TEntity]):
        self._repository = repository

    def exists_by_key(self, key: str) -> bool:
        return self._repository.entity_exists_by_key(key)

    def get_by_key(self, key: str) -> Optional[TEntity]:
        return self._repository.get_by_key(key)

    def save(self, entity: TEntity) -> None:
        self._repository.save(entity)

    def _get_non_null_by_key(self, key: str) -> TEntity:
        entity = self.get_by_key(key)
        if entity is None:
            raise EntityNotFoundException(
                "No item found for key={0}".format(key)
            )

        return entity
