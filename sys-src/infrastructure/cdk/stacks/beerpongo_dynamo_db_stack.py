from typing import Any

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct
from custom_types import DynamoDbStackConfig


class BeerpongoDynamoDbStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: DynamoDbStackConfig,
        **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        games_table_config = config["gamesTable"]

        # Create DynamoDB games table with 'GameId' as String partition key
        self.games_table = dynamodb.Table(
            self,
            id=games_table_config["id"],
            table_name=games_table_config["tableName"],
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(
                name="GameId", type=dynamodb.AttributeType.STRING
            ),
        )
