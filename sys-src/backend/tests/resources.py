from mypy_boto3_dynamodb import DynamoDBServiceResource

games_table_name = "TEST_GAMES_TABLE"


def create_games_table(dynamodb: DynamoDBServiceResource):
    dynamodb.create_table(
        TableName=games_table_name,
        KeySchema=[
            {"KeyType": "HASH", "AttributeName": "PK"},
            {"KeyType": "RANGE", "AttributeName": "SK"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    return dynamodb.Table(games_table_name)
