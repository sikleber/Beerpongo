import json
import logging
import os

import boto3


def on_update_game(event, context):
    body = json.loads(event['body'])
    current_connection_id = event["requestContext"]["connectionId"]
    table_name = os.environ["DB_TABLE"]
    table = boto3.resource("dynamodb").Table(table_name)

    if "GameId" not in body:
        return {'statusCode': 404, 'exception': 'No game id specified'}
    elif "State" not in body:
        return {'statusCode': 404, 'exception': 'No state specified'}

    game_id = body['GameId']
    state = body['State']

    # Get the item that will be changed
    data = table.get_item(
        Key={
            "GameId": game_id
        }
    )

    try:
        item = data['Item']
    # if item doesn't exist
    except KeyError:
        return {'statusCode': 400, 'exception': "Game not found"}
    except:
        return {'statusCode': 500, 'exception': "Error updating Game"}

    # update state string
    if len(item['State']) == 0:
        item['State'] += state
    else:
        item['State'] += "," + state

    # put item back into database
    try:
        table.put_item(Item=item)
    except Exception:
        return {'statusCode': 500, 'exception': "Error updating Game"}

    try:
        gatewayapi = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url="https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])
        message = json.dumps({"GameId": game_id, "State": item['State']}).encode('utf-8')

        for connection_id in item['ConnectionIds']:
            if connection_id != current_connection_id:
                try:
                    gatewayapi.post_to_connection(ConnectionId=connection_id, Data=message)
                except Exception:
                    logging.exception("Callback game connection failed")
    except Exception:
        logging.exception("Failed to callback game connections")

    return {'statusCode': 200}
