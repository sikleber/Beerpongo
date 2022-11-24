from websocket_lambdas.custom_types import WebsocketResponse


def on_connect(event: dict, context: dict) -> WebsocketResponse:
    return WebsocketResponse(statusCode=200)
