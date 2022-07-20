from aws_cdk import Stack
from aws_cdk.aws_apigatewayv2_alpha import WebSocketApi, WebSocketStage, WebSocketRouteOptions
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
from constructs import Construct


class BeerpongoApiGatewayWebsocketStack(Stack):
    def __init__(
            self, scope: Construct, construct_id: str, config: dict, route_lambdas: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        websocket_config = config["apiGatewayWebsocket"]
        self.web_socket_api = WebSocketApi(
            self,
            websocket_config["id"],
            api_name=websocket_config["name"],
            connect_route_options=WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration(
                    websocket_config["connectRoute"]["id"],
                    handler=route_lambdas["connectRoute"]
                ),
                authorizer=None,
            ),
            disconnect_route_options=WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration(
                    websocket_config["disconnectRoute"]["id"],
                    handler=route_lambdas["disconnectRoute"]
                ),
                authorizer=None,
            )
        )

        self.web_socket_stage = WebSocketStage(
            self,
            websocket_config["stage"]["id"],
            web_socket_api=self.web_socket_api,
            stage_name=websocket_config["stage"]["name"],
            auto_deploy=True
        )

        update_route_config = websocket_config["updateGameRoute"]
        self.web_socket_api.add_route(
            update_route_config["key"],
            integration=WebSocketLambdaIntegration(update_route_config["id"], route_lambdas["updateGameRoute"])
        )
