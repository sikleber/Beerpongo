from aws_cdk import Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import RemovalPolicy
from constructs import Construct


class BeerpongoDynamoDbStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dynamodb_config = config.get("dynamoDB")
        games_table_config = dynamodb_config.get("gamesTable")

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
