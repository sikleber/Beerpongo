import os

import pytest
from aws_cdk.assertions import Match, Template
from stacks.beerpongo_api_gateway_websocket_stack import (
    BeerpongoApiGatewayWebsocketStack,
)
from stacks.beerpongo_lambda_stack import BeerpongoLambdaStack


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"


@pytest.fixture
def lambda_stack(app, mock_config):
    yield BeerpongoLambdaStack(
        app,
        construct_id="BeerpongoLambdaStack",
        lambda_config=mock_config["lambdaStack"],
        dynamodb_config=mock_config["dynamodbStack"],
        cognito_user_pool_id="TEST_POOL_ID",
        cognito_user_pool_client_id="TEST_CLIENT_ID",
    )


@pytest.fixture
def route_lambdas(lambda_stack):
    yield {
        "createGameRoute": lambda_stack.lambda_on_create_game,
        "joinGameRoute": lambda_stack.lambda_on_join_game,
        "updateGameRoute": lambda_stack.lambda_on_update_game,
    }


@pytest.fixture
def auth_handler(lambda_stack):
    yield lambda_stack.lambda_authenticate_websocket


@pytest.fixture
def connect_handler(lambda_stack):
    yield lambda_stack.lambda_connect_websocket


@pytest.fixture
def websocket_stack(
    app, mock_config, route_lambdas, auth_handler, connect_handler
):
    yield BeerpongoApiGatewayWebsocketStack(
        app,
        construct_id="BeerpongoWebsocketStack",
        config=mock_config["apiGatewayWebsocketStack"],
        route_lambdas=route_lambdas,
        auth_handler=auth_handler,
        connect_handler=connect_handler,
    )


@pytest.fixture
def template(websocket_stack):
    yield Template.from_stack(websocket_stack)


def test_beerpongo_api_gateway_websocket_api(template: Template):
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Api",
        {
            "Name": "BeerpongoWebsocketApi",
            "ProtocolType": "WEBSOCKET",
            "RouteSelectionExpression": "$request.body.action",
        },
    )


def test_beerpongo_api_gateway_websocket_stage(template: Template):
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Stage",
        {
            "ApiId": {"Ref": "BeerpongoWebsocketStackIdDA88E1A0"},
            "StageName": "test",
            "AutoDeploy": True,
        },
    )


def test_beerpongo_api_gateway_websocket_create_game_route(template: Template):
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Route",
        {
            "ApiId": {"Ref": Match.any_value()},
            "RouteKey": "CreateGame",
            "AuthorizationType": "NONE",
            "Target": {
                "Fn::Join": [
                    "",
                    [
                        "integrations/",
                        {"Ref": Match.any_value()},
                    ],
                ]
            },
        },
    )


def test_beerpongo_api_gateway_websocket_join_game_route(template: Template):
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Route",
        {
            "ApiId": {"Ref": Match.any_value()},
            "RouteKey": "JoinGame",
            "AuthorizationType": "NONE",
            "Target": {
                "Fn::Join": [
                    "",
                    [
                        "integrations/",
                        {"Ref": Match.any_value()},
                    ],
                ]
            },
        },
    )


def test_beerpongo_api_gateway_websocket_update_game_route(template: Template):
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Route",
        {
            "ApiId": {"Ref": Match.any_value()},
            "RouteKey": "UpdateGame",
            "AuthorizationType": "NONE",
            "Target": {
                "Fn::Join": [
                    "",
                    [
                        "integrations/",
                        {"Ref": Match.any_value()},
                    ],
                ]
            },
        },
    )


def test_beerpongo_api_gateway_websocket_connect_route(template: Template):
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Route",
        {
            "ApiId": {"Ref": Match.any_value()},
            "RouteKey": "$connect",
            "AuthorizationType": "CUSTOM",
            "Target": {
                "Fn::Join": [
                    "",
                    [
                        "integrations/",
                        {"Ref": Match.any_value()},
                    ],
                ]
            },
        },
    )
