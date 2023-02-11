from abc import ABC
from typing import (
    Any,
    Generic,
    List,
    Mapping,
    Optional,
    TypedDict,
    TypeVar,
    cast,
)

from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb.service_resource import Table

from entities.base_entity import BaseRepository
from entities.custom_types import EntityNotFoundException


class Relation(TypedDict):
    pass


class RawRelation(TypedDict):
    PK: str
    SK: str


TRelation = TypeVar("TRelation", bound=Relation)
TRawRelation = TypeVar("TRawRelation", bound=RawRelation)


class RelationRepository(
    BaseRepository, Generic[TRawRelation, TRelation], ABC
):
    pk_prefix: str
    sk_prefix: str
    relation_pk_field: str
    relation_sk_field: str

    def __init__(
        self,
        table: Table,
        pk_prefix: str,
        sk_prefix: str,
        entity_pk_field: str,
        entity_sk_field: str,
    ) -> None:
        super().__init__(table)
        self.pk_prefix = pk_prefix
        self.sk_prefix = sk_prefix
        self.relation_pk_field = entity_pk_field
        self.relation_sk_field = entity_sk_field

    def relation_exists_by_keys(self, pk: str, sk: str) -> bool:
        data = self._table.get_item(
            Key={"PK": self.pk_prefix + pk, "SK": self.sk_prefix + sk}
        )

        return "Item" in data

    def get_by_keys(self, pk: str, sk: str) -> Optional[TRelation]:
        data = self._table.get_item(
            Key={"PK": self.pk_prefix + pk, "SK": self.sk_prefix + sk}
        )

        if "Item" in data:
            raw_entity: TRawRelation = cast(TRawRelation, data["Item"])
            return self._convert_raw(raw_entity)
        return None

    def get_all_by_pk(self, pk: str) -> List[TRelation]:
        data = self._table.query(
            KeyConditionExpression=(
                Key("PK").eq(pk) & Key("SK").begins_with(self.sk_prefix)
            )
        )

        raw_relations = cast(List[TRawRelation], data["Items"])

        return [self._convert_raw(r) for r in raw_relations]

    def save(self, entity: TRelation) -> None:
        raw_entity = self._convert_to_raw(entity)
        self._table.put_item(Item=cast(Mapping[str, str], raw_entity))

    def _convert_raw(self, raw_entity: TRawRelation) -> TRelation:
        entity = dict()
        entity[self.relation_pk_field] = raw_entity["PK"].replace(
            self.pk_prefix, ''
        )
        entity[self.relation_sk_field] = raw_entity["SK"].replace(
            self.sk_prefix, ''
        )
        for key in raw_entity:
            if key != "PK" and key != "SK":
                entity[key] = cast(Any, raw_entity)[key]

        return cast(TRelation, entity)

    def _convert_to_raw(self, entity: TRelation) -> TRawRelation:
        entity_copy = entity.copy()
        del entity_copy[self.relation_pk_field]
        del entity_copy[self.relation_sk_field]
        raw_entity = cast(TRawRelation, entity_copy)
        raw_entity["PK"] = (
            self.pk_prefix + cast(Any, entity)[self.relation_pk_field]
        )
        raw_entity["SK"] = (
            self.sk_prefix + cast(Any, entity)[self.relation_sk_field]
        )

        return cast(TRawRelation, raw_entity)


class RelationService(Generic[TRelation], ABC):
    def __init__(self, repository: RelationRepository[Any, TRelation]):
        self._repository = repository

    def exists_by_keys(self, pk: str, sk: str) -> bool:
        return self._repository.relation_exists_by_keys(pk, sk)

    def get_by_keys(self, pk: str, sk: str) -> Optional[TRelation]:
        return self._repository.get_by_keys(pk, sk)

    def get_all_by_pk(self, pk: str) -> List[TRelation]:
        return self._repository.get_all_by_pk(pk)

    def save(self, relation: TRelation) -> None:
        self._repository.save(relation)

    def _get_non_null_by_keys(self, pk: str, sk: str) -> TRelation:
        relation = self.get_by_keys(pk, sk)
        if relation is None:
            raise EntityNotFoundException(
                "No relation found for pk={0} and sk={1}".format(pk, sk)
            )

        return relation
