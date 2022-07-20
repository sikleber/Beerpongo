def on_update_game(event, context):
    print(str(event["body"]))

    return {
        "statusCode": 200
    }
