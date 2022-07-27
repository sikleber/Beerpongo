import json
import os

import boto3


def on_join_game(event, context):
    body = json.loads(event['body'])
    connection_id = event["requestContext"]["connectionId"]
    table_name = os.environ["DB_TABLE"]
    table = boto3.resource("dynamodb").Table(table_name)

    if "GameId" not in body:
        return {'statusCode': 404, 'exception': 'No game id specified'}

    game_id = body['GameId']

    data = table.get_item(
        Key={
            'GameId': game_id
        }
    )

    try:
        item = data['Item']
    except KeyError:
        return {"statusCode": "404"}

    item['PlayerCount'] += 1
    item['ConnectionIds'].append(connection_id)

    try:
        table.put_item(Item=item)
    except Exception:
        return {'statusCode': 500, 'exception': "Error receiving playerId"}

    return {
        "statusCode": "200",
        "body": json.dumps({
            "GameId": game_id, "PlayerId": item['PlayerCount'], "State": item["State"]
        })
    }
