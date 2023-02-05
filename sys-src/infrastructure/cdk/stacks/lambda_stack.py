from typing import Any, Dict, List, Sequence

import aws_cdk.aws_lambda as lambda_
from aws_cdk import Stack
from aws_cdk.aws_iam import PolicyStatement, ServicePrincipal
from constructs import Construct
from custom_types import LambdaStackConfig


class BeerpongoLambdaStack(Stack):
    lambdas: List[lambda_.Function] = list()

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_config: LambdaStackConfig,
        environment_variables: Dict[str, str],
        **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        lambdas_config = lambda_config["lambdas"]

        layer_config = lambda_config["layer"]
        self.dependency_lambda_layer = lambda_.LayerVersion(
            self,
            layer_config["id"],
            code=lambda_.Code.from_asset(layer_config["code"]),
            compatible_runtimes=[lambda_.Runtime(layer_config["runtime"])],
        )

        self.lambda_layers = [
            self.dependency_lambda_layer,
        ]

        initial_policy: Sequence[PolicyStatement] = [
            PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "execute-api:ManageConnections",
                ],
                resources=["*"],
            )
        ]

        authenticate_websocket_config = lambdas_config[
            "lambda_authenticate_websocket"
        ]
        connect_websocket_config = lambdas_config["lambda_on_connect"]
        create_game_config = lambdas_config["lambda_on_create_game"]
        join_game_config = lambdas_config["lambda_on_join_game"]
        guest_join_game_config = lambdas_config["lambda_on_join_game_as_guest"]
        update_game_config = lambdas_config["lambda_on_update_game"]

        # Create Websocket lambdas
        self.lambda_authenticate_websocket = lambda_.Function(
            self,
            id=authenticate_websocket_config["name"],
            runtime=lambda_.Runtime(authenticate_websocket_config["runtime"]),
            handler=authenticate_websocket_config["handler"],
            code=lambda_.Code.from_asset(
                authenticate_websocket_config["code"]
            ),
            layers=self.lambda_layers,
            environment=environment_variables,
            initial_policy=initial_policy,
        )
        self.lambdas.append(self.lambda_authenticate_websocket)

        self.lambda_connect_websocket = lambda_.Function(
            self,
            id=connect_websocket_config["name"],
            runtime=lambda_.Runtime(connect_websocket_config["runtime"]),
            handler=connect_websocket_config["handler"],
            code=lambda_.Code.from_asset(connect_websocket_config["code"]),
            layers=self.lambda_layers,
            environment=environment_variables,
            initial_policy=initial_policy,
        )
        self.lambdas.append(self.lambda_connect_websocket)

        self.lambda_on_create_game = lambda_.Function(
            self,
            id=create_game_config["name"],
            runtime=lambda_.Runtime(create_game_config["runtime"]),
            handler=create_game_config["handler"],
            code=lambda_.Code.from_asset(create_game_config["code"]),
            layers=self.lambda_layers,
            environment=environment_variables,
            initial_policy=initial_policy,
        )
        self.lambdas.append(self.lambda_on_create_game)

        self.lambda_on_join_game = lambda_.Function(
            self,
            id=join_game_config["name"],
            runtime=lambda_.Runtime(join_game_config["runtime"]),
            handler=join_game_config["handler"],
            code=lambda_.Code.from_asset(join_game_config["code"]),
            layers=self.lambda_layers,
            environment=environment_variables,
            initial_policy=initial_policy,
        )
        self.lambdas.append(self.lambda_on_join_game)

        self.lambda_on_join_game_as_guest = lambda_.Function(
            self,
            id=guest_join_game_config["name"],
            runtime=lambda_.Runtime(guest_join_game_config["runtime"]),
            handler=guest_join_game_config["handler"],
            code=lambda_.Code.from_asset(guest_join_game_config["code"]),
            layers=self.lambda_layers,
            environment=environment_variables,
            initial_policy=initial_policy,
        )
        self.lambdas.append(self.lambda_on_join_game_as_guest)

        self.lambda_on_update_game = lambda_.Function(
            self,
            id=update_game_config["name"],
            runtime=lambda_.Runtime(update_game_config["runtime"]),
            handler=update_game_config["handler"],
            code=lambda_.Code.from_asset(update_game_config["code"]),
            layers=self.lambda_layers,
            environment=environment_variables,
            initial_policy=initial_policy,
        )
        self.lambdas.append(self.lambda_on_update_game)

        self.lambda_authenticate_websocket.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-authenticate-permission",
        )

        self.lambda_connect_websocket.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-connect-permission",
        )

        self.lambda_on_create_game.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-create-game-permission",
        )

        self.lambda_on_join_game.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-join-game-permission",
        )

        self.lambda_on_join_game_as_guest.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-join-game-as-guest-permission",
        )

        self.lambda_on_update_game.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-update-game-permission",
        )
