import json
import logging
import os
import random
import string

import boto3

alphabet = string.ascii_letters + string.digits


def _generate_game_id():
    """
    :return: a randomly generated game id string with 8 characters
    """
    return "".join(random.choices(alphabet, k=8))


def on_create_game(event, context):
    """
    Creates and puts a new Game item into dynamodb table.

    Initial Game item values:
        GameId: a randomly generated 8 character string
        State:  empty string
        PlayerCount: 1
        ConnectionIds: a list with the current connectionId as its only value

    :param:  event:   the lambda call event containing all given parameters
    :param:  context: the lambda call context
    :return: JSON with Status Code and game information as body
            200	Create ok
            500 Error creating the Game item
    """
    connection_id = event["requestContext"]["connectionId"]
    table_name = os.environ["DB_TABLE"]
    body = json.loads(event["body"])

    # set game id if present, else generate one
    if "GameId" in body:
        game_id = body["GameId"]
    else:
        game_id = _generate_game_id()

    table = boto3.resource("dynamodb").Table(table_name)

    try:
        # check if game item with given id already exists
        data = table.get_item(Key={"GameId": game_id})
        if "Item" in data:
            raise "Game item with id=%s already exists" % game_id

        # put new item into database
        new_game = {
            "GameId": game_id,
            "State": "",
            "PlayerCount": 1,
            "ConnectionIds": [connection_id],
        }
        table.put_item(Item=new_game)
        logging.debug("Created new game: %s", new_game)

        return {"statusCode": 200, "body": json.dumps({"GameId": game_id})}
    except Exception:
        logging.exception("Failed to put new game item")
        return {"statusCode": 500}
