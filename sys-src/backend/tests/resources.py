games_table_name = "TEST_GAMES_TABLE"


def create_games_table(dynamodb):
    dynamodb.create_table(
        TableName=games_table_name,
        KeySchema=[
            {"KeyType": "HASH", "AttributeName": "GameId"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "GameId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    return dynamodb.Table(games_table_name)
