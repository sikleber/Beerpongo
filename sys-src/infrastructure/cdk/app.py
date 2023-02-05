#!/usr/bin/env python3
import logging
from typing import Optional, cast

import aws_cdk
import aws_cdk as cdk
import yaml
from custom_types import CdkConfig, RouteLambdas
from stacks.api_gateway_websocket_stack import (
    BeerpongoApiGatewayWebsocketStack,
)
from stacks.cognito_stack import BeerpongoCognitoStack
from stacks.dynamo_db_stack import BeerpongoDynamoDbStack
from stacks.lambda_stack import BeerpongoLambdaStack

_logger = logging.getLogger("app")


def get_config(cdk_app: aws_cdk.App) -> Optional[CdkConfig]:
    """
    Reads the config yaml file for the given environment.
    Used to switch between dev and prod environments.

    :return: The CDK config
    """
    c: Optional[CdkConfig] = None
    env = None
    try:
        env = cdk_app.node.try_get_context("config")
        with open(
            file="./config/default.yaml", mode="r", encoding="utf8"
        ) as file:
            try:
                content = file.read()
                content = content.replace("{CONFIG_NAME}", env)
                c = cast(CdkConfig, yaml.safe_load(content))
                c["configName"] = env
            except yaml.YAMLError as e:
                _logger.error(e)
    except Exception as e:
        raise Exception(
            f"""No or no valid config variable passed!
             '-c config={env}'\n {e}"""
        )

    return c


app = cdk.App()
config = get_config(app)

if config is None:
    _logger.error("No config loaded")
else:
    default_env = {'region': config["region"]}

    # Create DynamoDB stack
    DynamoDbStack = BeerpongoDynamoDbStack(
        app,
        config["dynamodbStack"]["stackName"],
        config["dynamodbStack"],
        env=default_env,
    )

    # Create Cognito stack
    CognitoStack = BeerpongoCognitoStack(
        app,
        config["cognitoStack"]["stackName"],
        config["cognitoStack"],
        env=default_env,
    )

    # Create Lambda stack
    LambdaStack = BeerpongoLambdaStack(
        app,
        config["lambdaStack"]["stackName"],
        lambda_config=config["lambdaStack"],
        env=default_env,
        environment_variables={
            "USER_POOL_ID": CognitoStack.user_pool.user_pool_id,
            "APP_CLIENT_ID": CognitoStack.user_pool_client.user_pool_client_id,
            "DB_TABLE": DynamoDbStack.table.table_name,
        },
    )

    # Create API-Gateway websocket stack
    ApiGatewayStack = BeerpongoApiGatewayWebsocketStack(
        app,
        config["apiGatewayWebsocketStack"]["stackName"],
        config["apiGatewayWebsocketStack"],
        env=default_env,
        route_lambdas=RouteLambdas(
            createGameRoute=LambdaStack.lambda_on_create_game,
            joinGameRoute=LambdaStack.lambda_on_join_game,
            joinAsGuestGameRoute=LambdaStack.lambda_on_join_game_as_guest,
            updateGameRoute=LambdaStack.lambda_on_update_game,
        ),
        auth_handler=LambdaStack.lambda_authenticate_websocket,
        connect_handler=LambdaStack.lambda_connect_websocket,
    )

    app.synth()
