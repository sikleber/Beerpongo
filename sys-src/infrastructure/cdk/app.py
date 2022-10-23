#!/usr/bin/env python3
import logging

import aws_cdk as cdk
import yaml
from stacks.beerpongo_api_gateway_websocket_stack import (
    BeerpongoApiGatewayWebsocketStack,
)
from stacks.beerpongo_cognito_stack import BeerpongoCognitoStack
from stacks.beerpongo_dynamo_db_stack import BeerpongoDynamoDbStack
from stacks.beerpongo_lambda_stack import BeerpongoLambdaStack

_logger = logging.getLogger("app")


def get_config():
    """
    Reads the config yaml file for the given environment.
    Used to switch between dev and prod environments.

    :return: a dict object.
    """
    env = None
    try:
        env = app.node.try_get_context("config")
        with open(
            file="./config/" + env + ".yaml", mode="r", encoding="utf8"
        ) as stream:
            try:
                c = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                _logger.error(e)
        c["config_name"] = env

        return c
    except Exception as e:
        _logger.error(
            f"""No or no valid config variable passed!
             '-c config={env}'\n {e}"""
        )


app = cdk.App()
config = get_config()

# Create DynamoDB stack
BeerpongoDynamoDbStack(app, config["dynamoDB"]["stackName"], config)

# Create Cognito stack
CognitoStack = BeerpongoCognitoStack(app, config["cognito"]["stackName"], config)

# Create Lambda stack
LambdaStack = BeerpongoLambdaStack(
    app,
    config["lambda"]["stackName"],
    config,
    cognito_user_pool_id=CognitoStack.user_pool.user_pool_id,
    cognito_user_pool_client_id=CognitoStack.user_pool_client.user_pool_client_id
)

# Create API-Gateway websocket stack
BeerpongoApiGatewayWebsocketStack(
    app,
    config["apiGatewayWebsocket"]["stackName"],
    config,
    route_lambdas={
        "createGameRoute": LambdaStack.lambda_on_create_game,
        "joinGameRoute": LambdaStack.lambda_on_join_game,
        "updateGameRoute": LambdaStack.lambda_on_update_game,
    },
    auth_handler=LambdaStack.lambda_authenticate_websocket,
    connect_handler=LambdaStack.lambda_connect_websocket
)

app.synth()
