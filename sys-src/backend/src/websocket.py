import logging
from typing import List

from mypy_boto3_apigatewaymanagementapi.client import (
    ApiGatewayManagementApiClient,
)


class WebsocketService:
    def __init__(self, api_client: ApiGatewayManagementApiClient) -> None:
        self._api_client = api_client

    def callback_websocket_connections(
        self,
        connection_ids: List[str],
        callback_data: str,
    ) -> None:
        for connection_id in connection_ids:
            try:
                self._api_client.post_to_connection(
                    ConnectionId=connection_id, Data=callback_data
                )
            except Exception:
                logging.exception(
                    "Callback websocket connection with "
                    "connectionId={0} failed".format(connection_id)
                )
