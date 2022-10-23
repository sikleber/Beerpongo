import aws_cdk.aws_lambda as lambda_
from aws_cdk import Stack
from aws_cdk.aws_iam import PolicyStatement, ServicePrincipal
from constructs import Construct


class BeerpongoLambdaStack(Stack):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            config: dict,
            cognito_user_pool_id: str,
            cognito_user_pool_client_id: str,
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read the config
        dynamodb_config = config.get("dynamoDB")
        games_table_config = dynamodb_config.get("gamesTable")
        lambda_config = config.get("lambda")

        # Create Websocket lambdas
        authenticate_websocket_config = lambda_config.get("lambdas").get(
            "lambda_authenticate_websocket"
        )
        connect_websocket_config = lambda_config.get("lambdas").get(
            "lambda_on_connect"
        )
        create_game_config = lambda_config.get("lambdas").get(
            "lambda_on_create_game"
        )
        join_game_config = lambda_config.get("lambdas").get(
            "lambda_on_join_game"
        )
        update_game_config = lambda_config.get("lambdas").get(
            "lambda_on_update_game"
        )

        self.jwt_lambda_layer = lambda_.LayerVersion(
            self,
            authenticate_websocket_config["jwt_layer"]["id"],
            code=lambda_.Code.from_asset(authenticate_websocket_config["jwt_layer"]["code"]),
            compatible_runtimes=[lambda_.Runtime(authenticate_websocket_config["runtime"])]
        )

        self.lambda_authenticate_websocket = lambda_.Function(
            self,
            id=authenticate_websocket_config["name"],
            runtime=lambda_.Runtime(authenticate_websocket_config["runtime"]),
            handler=authenticate_websocket_config["handler"],
            code=lambda_.Code.from_asset(
                authenticate_websocket_config["code"]
            ),
            environment={
                "USER_POOL_ID": cognito_user_pool_id,
                "APP_CLIENT_ID": cognito_user_pool_client_id
            },
            layers=[self.jwt_lambda_layer]
        )

        self.lambda_connect_websocket = lambda_.Function(
            self,
            id=connect_websocket_config["name"],
            runtime=lambda_.Runtime(connect_websocket_config["runtime"]),
            handler=connect_websocket_config["handler"],
            code=lambda_.Code.from_asset(
                connect_websocket_config["code"]
            ),
        )

        self.lambda_on_create_game = lambda_.Function(
            self,
            id=create_game_config["name"],
            runtime=lambda_.Runtime(create_game_config["runtime"]),
            handler=create_game_config["handler"],
            code=lambda_.Code.from_asset(create_game_config["code"]),
            environment={"DB_TABLE": games_table_config["tableName"]},
        )

        self.lambda_on_join_game = lambda_.Function(
            self,
            id=join_game_config["name"],
            runtime=lambda_.Runtime(join_game_config["runtime"]),
            handler=join_game_config["handler"],
            code=lambda_.Code.from_asset(join_game_config["code"]),
            environment={"DB_TABLE": games_table_config["tableName"]},
        )

        self.lambda_on_update_game = lambda_.Function(
            self,
            id=update_game_config["name"],
            runtime=lambda_.Runtime(update_game_config["runtime"]),
            handler=update_game_config["handler"],
            code=lambda_.Code.from_asset(update_game_config["code"]),
            environment={"DB_TABLE": games_table_config["tableName"]},
        )

        self.lambda_on_create_game.add_to_role_policy(
            PolicyStatement(
                actions=["dynamodb:GetItem", "dynamodb:PutItem"],
                resources=["*"],
            )
        )

        self.lambda_on_join_game.add_to_role_policy(
            PolicyStatement(
                actions=["dynamodb:GetItem", "dynamodb:PutItem"],
                resources=["*"],
            )
        )

        self.lambda_on_update_game.add_to_role_policy(
            PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    'execute-api:ManageConnections',
                ],
                resources=["*"],
            )
        )

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

        self.lambda_on_update_game.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-ws-update-game-permission",
        )
