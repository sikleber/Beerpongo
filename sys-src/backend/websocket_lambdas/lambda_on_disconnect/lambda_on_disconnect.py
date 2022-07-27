def on_disconnect(event, context):
    print(str(event))

    return {
        "statusCode": 200
    }