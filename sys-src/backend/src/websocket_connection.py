import logging
from typing import Dict, List

import boto3


class RequestContext(Dict):
    domainName: str
    stage: str


def callback_websocket_connections(
    request_context: RequestContext,
    connection_ids: List[str],
    callback_data: str,
) -> None:
    endpoint_url = "https://{0}/{1}".format(
        request_context["domainName"],
        request_context["stage"],
    )
    gatewayapi = boto3.client(
        "apigatewaymanagementapi", endpoint_url=endpoint_url
    )

    for connection_id in connection_ids:
        try:
            gatewayapi.post_to_connection(
                ConnectionId=connection_id, Data=callback_data
            )
        except Exception:
            logging.exception(
                "Callback websocket connection with "
                "connectionId={0} failed".format(connection_id)
            )
