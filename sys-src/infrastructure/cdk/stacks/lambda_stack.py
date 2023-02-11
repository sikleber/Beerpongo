import hashlib
import json
from typing import Any, Dict, List, Sequence

import aws_cdk.aws_lambda as lambda_
import constants
from aws_cdk import AssetHashType, Stack
from aws_cdk.aws_iam import PolicyStatement, ServicePrincipal
from constructs import Construct
from custom_types import LambdaStackConfig


def _get_lock_file_hash(pipenv_dir: str) -> str:
    with open(pipenv_dir + "/Pipfile.lock", mode='r', encoding='utf-8') as f:
        lock_file = json.load(f)
        lock_file_str = f'{json.dumps(lock_file["default"])}'
    return hashlib.sha256(lock_file_str.encode('utf-8')).hexdigest()


class BeerpongoLambdaStack(Stack):
    lambdas: List[lambda_.Function] = list()

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_config: LambdaStackConfig,
        environment_variables: Dict[str, str],
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        lambdas_config = lambda_config["lambdas"]

        layer_config = lambda_config["layer"]
        self.python_lambda_layer = lambda_.LayerVersion(
            self,
            layer_config["id"],
            code=lambda_.Code.from_asset(
                layer_config["sourcesDir"],
                asset_hash_type=AssetHashType.CUSTOM,
                asset_hash=_get_lock_file_hash(layer_config["pipenvDir"]),
                exclude=['requirements.txt'],
            ),
            compatible_runtimes=[constants.RUNTIME],
            compatible_architectures=[constants.ARCHITECTURE],
        )

        self.lambda_layers = [
            self.python_lambda_layer,
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

        handler = "websocket_handler.handler"
        code = lambda_.Code.from_asset("./../backend/src")

        # Create Websocket lambdas
        self.lambda_authenticate_websocket = lambda_.Function(
            self,
            id=authenticate_websocket_config["name"],
            runtime=constants.RUNTIME,
            handler=handler,
            code=code,
            layers=self.lambda_layers,
            environment=dict(
                environment_variables, **{"HANDLER": "AUTHENTICATE"}
            ),
            initial_policy=initial_policy,
            architecture=constants.ARCHITECTURE,
        )
        self.lambdas.append(self.lambda_authenticate_websocket)

        self.lambda_connect_websocket = lambda_.Function(
            self,
            id=connect_websocket_config["name"],
            runtime=constants.RUNTIME,
            handler=handler,
            code=code,
            layers=self.lambda_layers,
            environment=dict(environment_variables, **{"HANDLER": "CONNECT"}),
            initial_policy=initial_policy,
            architecture=constants.ARCHITECTURE,
        )
        self.lambdas.append(self.lambda_connect_websocket)

        self.lambda_on_create_game = lambda_.Function(
            self,
            id=create_game_config["name"],
            runtime=constants.RUNTIME,
            handler=handler,
            code=code,
            layers=self.lambda_layers,
            environment=dict(
                environment_variables, **{"HANDLER": "CREATE_GAME"}
            ),
            initial_policy=initial_policy,
            architecture=constants.ARCHITECTURE,
        )
        self.lambdas.append(self.lambda_on_create_game)

        self.lambda_on_join_game = lambda_.Function(
            self,
            id=join_game_config["name"],
            runtime=constants.RUNTIME,
            handler=handler,
            code=code,
            layers=self.lambda_layers,
            environment=dict(
                environment_variables, **{"HANDLER": "JOIN_GAME"}
            ),
            initial_policy=initial_policy,
            architecture=constants.ARCHITECTURE,
        )
        self.lambdas.append(self.lambda_on_join_game)

        self.lambda_on_join_game_as_guest = lambda_.Function(
            self,
            id=guest_join_game_config["name"],
            runtime=constants.RUNTIME,
            handler=handler,
            code=code,
            layers=self.lambda_layers,
            environment=dict(
                environment_variables, **{"HANDLER": "JOIN_GAME_AS_GUEST"}
            ),
            initial_policy=initial_policy,
            architecture=constants.ARCHITECTURE,
        )
        self.lambdas.append(self.lambda_on_join_game_as_guest)

        self.lambda_on_update_game = lambda_.Function(
            self,
            id=update_game_config["name"],
            runtime=constants.RUNTIME,
            handler=handler,
            code=code,
            layers=self.lambda_layers,
            environment=dict(
                environment_variables, **{"HANDLER": "UPDATE_GAME"}
            ),
            initial_policy=initial_policy,
            architecture=constants.ARCHITECTURE,
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
