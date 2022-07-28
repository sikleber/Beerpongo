import json
import os

import boto3


def put(event, context):
    """
    Provide an event, that contains the following keys:
        - id: GameId composed of 8 characters
        - state in the form '[ID]:[0-9, X]'

    Requires a role with read/write access to DynamoDB.

    :param:  event: the lambda call event containing all given parameters
    :param:  context: the lambda call context
    :return: response: JSON with http Status Code
            200	Update ok
            400	Invalid ID supplied
            500 Error updating game state
    """
    table_name = os.environ['DB_TABLE']

    id = event['id']
    state = event['state']

    # Define access to db
    table = boto3.resource("dynamodb").Table(table_name)

    # Get the item that will be changed
    data = table.get_item(Key={"GameId": id})

    try:
        item = data['Item']

    # if item doesn't exist
    except KeyError:
        return {'statusCode': 400, 'exception': "Game not found"}
    except Exception:
        return {'statusCode': 500, 'exception': "Error updating Game"}

    # get length of state
    len_state = len(item['State'])

    # update state string
    if len_state == 0:
        item['State'] += state
    else:
        item['State'] += "," + state

    # put item back into database
    try:
        table.put_item(Item=item)

    except Exception:
        return {'statusCode': 500, 'exception': "Error updating Game"}

    # if all went well
    response = {
        'statusCode': 200,
        'body': json.dumps({"message": f"Game State of Game {id} updated"}),
    }

    return response
