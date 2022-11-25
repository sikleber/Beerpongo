#!/usr/bin/env python3
import logging
from typing import cast

import aws_cdk
import aws_cdk as cdk
import yaml
from custom_types import CdkConfig, RouteLambdas
from stacks.beerpongo_api_gateway_websocket_stack import (
    BeerpongoApiGatewayWebsocketStack,
)
from stacks.beerpongo_cognito_stack import BeerpongoCognitoStack
from stacks.beerpongo_dynamo_db_stack import BeerpongoDynamoDbStack
from stacks.beerpongo_lambda_stack import BeerpongoLambdaStack

_logger = logging.getLogger("app")


def get_config(cdk_app: aws_cdk.App) -> CdkConfig | None:
    """
    Reads the config yaml file for the given environment.
    Used to switch between dev and prod environments.

    :return: The CDK config
    """
    c: CdkConfig | None = None
    env = None
    try:
        env = cdk_app.node.try_get_context("config")
        with open(
            file="./config/" + env + ".yaml", mode="r", encoding="utf8"
        ) as stream:
            try:
                c = cast(CdkConfig, yaml.safe_load(stream))
                c["configName"] = env
            except yaml.YAMLError as e:
                _logger.error(e)
    except Exception as e:
        raise f"""No or no valid config variable passed!
             '-c config={env}'\n {e}"""

    return c


app = cdk.App()
config = get_config(app)

if config is None:
    _logger.error("No config loaded")
else:
    # Create DynamoDB stack
    BeerpongoDynamoDbStack(
        app, config["dynamodbStack"]["stackName"], config["dynamodbStack"]
    )

    # Create Cognito stack
    CognitoStack = BeerpongoCognitoStack(
        app, config["cognitoStack"]["stackName"], config["cognitoStack"]
    )

    # Create Lambda stack
    LambdaStack = BeerpongoLambdaStack(
        app,
        config["lambdaStack"]["stackName"],
        lambda_config=config["lambdaStack"],
        dynamodb_config=config["dynamodbStack"],
        cognito_user_pool_id=CognitoStack.user_pool.user_pool_id,
        cognito_user_pool_client_id=CognitoStack.user_pool_client.user_pool_client_id,
    )

    # Create API-Gateway websocket stack
    BeerpongoApiGatewayWebsocketStack(
        app,
        config["apiGatewayWebsocketStack"]["stackName"],
        config["apiGatewayWebsocketStack"],
        route_lambdas=RouteLambdas(
            createGameRoute=LambdaStack.lambda_on_create_game,
            joinGameRoute=LambdaStack.lambda_on_join_game,
            updateGameRoute=LambdaStack.lambda_on_update_game,
        ),
        auth_handler=LambdaStack.lambda_authenticate_websocket,
        connect_handler=LambdaStack.lambda_connect_websocket,
    )

    app.synth()
