import os

import boto3


def join(event, context):
    """
    Increments the playerCount in the gameTable and
    sends the incremented ID back to the player.
    Requires a role with read/write access to DynamoDB.

     Provide an event, that contains the following keys in 'params:path':
        - GameId

    :param:  event: the lambda call event containing all given parameters
    :param:  context: the lambda call context
    :return: response: JSON with http Status Code
            200	Incremete playerID ok
            500 Error receiving id
            404 Error gameId not found
    """

    table_name = os.environ["DB_TABLE"]

    client = boto3.resource("dynamodb")
    table = client.Table(table_name)

    game_id = event['params']['path']['GameId']

    data = table.get_item(Key={'GameId': game_id})

    try:
        item = data['Item']
    except KeyError:
        return {"statusCode": "404"}

    item['PlayerCount'] += 1

    try:
        table.put_item(Item=item)

    except Exception:
        return {'statusCode': 500, 'exception': "Error receiving playerId"}

    response = {
        "statusCode": "200",
        "body": {"id": game_id, "playerid": item['PlayerCount']},
    }

    return response
