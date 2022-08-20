import json
import logging
import os

import boto3


def on_join_game(event, context):
    """
    Increments the playerCount in the gameTable and sends the incremented ID
    back to the player. Adds the event connectionId to the list of connections
    to callback on state update.

    :param:  event:   the lambda call event containing all given parameters
    :param:  context: the lambda call context
    :return: JSON with Status Code and game information as body
            200	Create ok
            404 Game not found
            500 Error changing the Game item
    """
    body = json.loads(event["body"])
    connection_id = event["requestContext"]["connectionId"]
    table_name = os.environ["DB_TABLE"]
    table = boto3.resource("dynamodb").Table(table_name)

    try:
        if "GameId" not in body:
            raise "No game id specified in event body={0}".format(body)

        game_id = body["GameId"]
        data = table.get_item(Key={"GameId": game_id})

        if "Item" not in data:
            raise "No item found for GameId={0}".format(game_id)
    except Exception:
        logging.exception("Failed to get game item by id")
        return {"statusCode": 404}

    try:
        item = data["Item"]
        item["PlayerCount"] += 1
        item["ConnectionIds"].append(connection_id)
        table.put_item(Item=item)
    except Exception:
        logging.exception("Failed to put changed game item")
        return {"statusCode": 500}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "GameId": game_id,
                "PlayerCount": str(item["PlayerCount"]),
                "State": item["State"],
            }
        ),
    }
