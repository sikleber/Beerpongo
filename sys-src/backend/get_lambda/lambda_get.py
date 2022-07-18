import boto3
import os



def get(event, context):
    """
    Provide an event, that contains the following keys in 'params:path':
        - GameId

    Requires a role with reading access to DynamoDB.

    :param:  event: the lambda call event containing all given parameters
    :param:  context: the lambda call context
    :return response: JSON containing a statusCode and the body
            with the gameID, playerCount and the current state of the game
    """
    table_name = os.environ['DB_TABLE']


    # Defining access to database
    res = boto3.resource("dynamodb")
    table = res.Table(table_name)

    # Getting item for id given by the event
    item_id = event['params']['path']['GameId']

    data = table.get_item(
        Key={
            'GameId': item_id
        }
    )

    try:
        item = data['Item']
    except KeyError:
        return {"statusCode": 404}

    response = {
        "statusCode": 200,
        "body": item
    }

    return response