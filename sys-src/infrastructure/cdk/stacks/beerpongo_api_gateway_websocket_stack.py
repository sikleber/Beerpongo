from aws_cdk import Stack
from aws_cdk.aws_apigatewayv2 import CfnRouteResponse
from aws_cdk.aws_apigatewayv2_alpha import (
    WebSocketApi,
    WebSocketStage,
    WebSocketRouteOptions,
)
from aws_cdk.aws_apigatewayv2_authorizers_alpha import (
    WebSocketLambdaAuthorizer,
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import (
    WebSocketLambdaIntegration,
)
from aws_cdk.aws_lambda import IFunction
from constructs import Construct


class BeerpongoApiGatewayWebsocketStack(Stack):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            config: dict,
            route_lambdas: dict,
            auth_handler: IFunction,
            connect_handler: IFunction,
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        websocket_config = config["apiGatewayWebsocket"]

        self.web_socket_api = WebSocketApi(
            self,
            websocket_config["id"],
            api_name=websocket_config["name"],
        )

        self.web_socket_stage = WebSocketStage(
            self,
            websocket_config["stage"]["id"],
            web_socket_api=self.web_socket_api,
            stage_name=websocket_config["stage"]["name"],
            auto_deploy=True,
        )

        self.authorizer = WebSocketLambdaAuthorizer(
            id=websocket_config["authorizerId"],
            handler=auth_handler,
            identity_source=[
                'route.request.header.Authorization',
            ],
        )

        self.web_socket_api.add_route(
            route_key="$connect",
            integration=WebSocketLambdaIntegration(
                websocket_config["connectRouteIntegrationId"],
                connect_handler
            ),
            authorizer=self.authorizer
        )

        create_game_route_config = websocket_config["createGameRoute"]
        self.creat_game_route = self.web_socket_api.add_route(
            create_game_route_config["key"],
            integration=WebSocketLambdaIntegration(
                create_game_route_config["id"],
                route_lambdas["createGameRoute"],
            ),
        )

        join_game_route_config = websocket_config["joinGameRoute"]
        self.join_game_route = self.web_socket_api.add_route(
            join_game_route_config["key"],
            integration=WebSocketLambdaIntegration(
                join_game_route_config["id"], route_lambdas["joinGameRoute"]
            ),
        )

        update_game_route_config = websocket_config["updateGameRoute"]
        self.update_game_route = self.web_socket_api.add_route(
            update_game_route_config["key"],
            integration=WebSocketLambdaIntegration(
                update_game_route_config["id"],
                route_lambdas["updateGameRoute"],
            ),
        )

        CfnRouteResponse(
            self,
            create_game_route_config["responseId"],
            api_id=self.web_socket_api.api_id,
            route_id=self.creat_game_route.route_id,
            route_response_key="$default",
        )

        CfnRouteResponse(
            self,
            join_game_route_config["responseId"],
            api_id=self.web_socket_api.api_id,
            route_id=self.join_game_route.route_id,
            route_response_key="$default",
        )

        CfnRouteResponse(
            self,
            update_game_route_config["responseId"],
            api_id=self.web_socket_api.api_id,
            route_id=self.update_game_route.route_id,
            route_response_key="$default",
        )
