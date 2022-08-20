import json
import logging
import os

import boto3


def on_update_game(event, context):
    """
    Update the game state by a given string and callback all game
    connections specified by the list of connection ids in the game item.

    :param: event:   the lambda call event containing all given parameters
    :param: context: the lambda call context
    :return: JSON with Status Code and game information as body
            200	Update ok
            404 Game not found
            500 Error changing the Game item
    """
    body = json.loads(event["body"])
    current_connection_id = event["requestContext"]["connectionId"]
    table_name = os.environ["DB_TABLE"]
    table = boto3.resource("dynamodb").Table(table_name)

    try:
        if "GameId" not in body:
            raise "No game id specified in body={0}".format(body)
        elif "State" not in body:
            raise "No state specified in body={0}".format(body)

        game_id = body["GameId"]
        state = body["State"]

        # Get the item that will be changed
        data = table.get_item(Key={"GameId": game_id})
        if "Item" not in data:
            raise "No item found for GameId={0}".format(game_id)
    except Exception:
        return {"statusCode": 404}

    try:
        # update state string
        item = data["Item"]
        if len(item["State"]) == 0:
            item["State"] += state
        else:
            item["State"] += "," + state

        # update dynamodb
        table.put_item(Item=item)
    except Exception:
        logging.exception("Failed to update game item")
        return {"statusCode": 500}

    response_data = json.dumps({"GameId": game_id, "State": item["State"]})

    # callback game connections
    try:
        endpoint_url = "https://{0}/{1}".format(
            event["requestContext"]["domainName"],
            event["requestContext"]["stage"],
        )
        gatewayapi = boto3.client(
            "apigatewaymanagementapi", endpoint_url=endpoint_url
        )

        for connection_id in item["ConnectionIds"]:
            if connection_id != current_connection_id:
                try:
                    gatewayapi.post_to_connection(
                        ConnectionId=connection_id, Data=response_data
                    )
                except Exception:
                    logging.exception(
                        "Callback game connection with "
                        "connectionId={0} failed".format(connection_id)
                    )
    except Exception:
        logging.exception("Failed to callback game connections")

    return {"statusCode": 200, "body": response_data}