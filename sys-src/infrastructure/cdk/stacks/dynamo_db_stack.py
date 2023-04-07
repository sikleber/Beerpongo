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

        table_config = config["table"]

        # Create DynamoDB table with 'PK' partition key as String
        # and 'SK' as sort key String
        self.table = dynamodb.Table(
            self,
            id=table_config["id"],
            table_name=table_config["tableName"],
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK", type=dynamodb.AttributeType.STRING
            ),
        )

        # Add global secondary index
        # with 'SK' as partition key and 'PK' as sort key
        self.table.add_global_secondary_index(
            index_name=table_config['gsiIndex'],
            partition_key=dynamodb.Attribute(name='SK', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='PK', type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )
