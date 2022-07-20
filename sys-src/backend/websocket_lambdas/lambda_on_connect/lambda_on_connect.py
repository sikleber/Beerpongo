def on_connect(event, context):
    print("ConnectionId: " + str(event["requestContext"]["connectionId"]))

    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    connection_id = event["requestContext"]["connectionId"]
    callback_url = 'https://{}/{}/@connections/{}'.format(domain, stage, connection_id)
    print(callback_url)

    return {
        "statusCode": 200
    }
