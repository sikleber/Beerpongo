import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from aws_cdk.aws_s3_assets import Asset

from stacks.beerpongo_lambda_stack import BeerpongoLambdaStack


@pytest.fixture
def app():
    yield App()


@pytest.fixture
def mock_config():
    yield {
        "dynamoDB": {
            "stackName": 'BeerpongoDynamoDbStackDev',
            "gamesTable": {
                "id": 'BeerpongoDevGamesTable',
                "tableName": 'BeerpongoDevGamesTable',
            },
        },
        "lambda": {
            "stackName": "LambdaStackDev",
            "lambdas": {
                "lambda_authenticate_websocket": {
                    "name": "lambdaDev_authenticate_websocket",
                    "code": "./../backend/websocket_lambdas",
                    "handler": "lambda_authenticate_websocket.on_connect",
                    "runtime": 'python3.9',
                    "jwt_layer": {
                        "id": "py39_jwt_authentication_layer",
                        "code": "./../backend/lambda_layers/pyjwtcrypto_39.zip"
                    }
                },
                "lambda_on_connect": {
                    "name": "lambdaDev_connect_websocket",
                    "code": "./../backend/websocket_lambdas",
                    "handler": "lambda_on_connect.on_connect",
                    "runtime": 'python3.9',
                },
                "lambda_on_create_game": {
                    "name": "lambdaDev_createGame",
                    "code": "./../backend/websocket_lambdas",
                    "handler": "lambda_on_create_game.on_create_game",
                    "runtime": "python3.9",
                },
                "lambda_on_join_game": {
                    "name": "lambdaDev_joinGame",
                    "code": "./../backend/websocket_lambdas",
                    "handler": "lambda_on_join_game.on_join_game",
                    "runtime": "python3.9",
                },
                "lambda_on_update_game": {
                    "name": "lambdaDev_updateGame",
                    "code": "./../backend/websocket_lambdas",
                    "handler": "lambda_on_update_game.on_update_game",
                    "runtime": "python3.9",
                },
            },
        },
    }


@pytest.fixture
def lambda_stack(app, mock_config):
    yield BeerpongoLambdaStack(
        app,
        construct_id="BeerpongoLambdaStack",
        config=mock_config,
        cognito_user_pool_id="TEST_POOL_ID",
        cognito_user_pool_client_id="TEST_CLIENT_ID"
    )


@pytest.fixture
def template(lambda_stack):
    yield Template.from_stack(lambda_stack)


def test_create_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_create_game = Asset(
        lambda_stack,
        "lambda_on_create_game",
        path="./../backend/websocket_lambdas/",
    )
    lambda_on_create_game_name = lambda_stack.resolve(
        asset_lambda_on_create_game.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "lambda_on_create_game.on_create_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_create_game_name,
                "S3Key": asset_lambda_on_create_game.s3_object_key,
            },
        },
    )


def test_join_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_join_game = Asset(
        lambda_stack,
        "lambda_on_join_game",
        path="./../backend/websocket_lambdas/",
    )
    lambda_on_join_game_name = lambda_stack.resolve(
        asset_lambda_on_join_game.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "lambda_on_join_game.on_join_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_join_game_name,
                "S3Key": asset_lambda_on_join_game.s3_object_key,
            },
        },
    )


def test_update_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_update_game = Asset(
        lambda_stack,
        "lambda_on_update_game",
        path="./../backend/websocket_lambdas/",
    )
    lambda_on_update_game_name = lambda_stack.resolve(
        asset_lambda_on_update_game.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "lambda_on_update_game.on_update_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_update_game_name,
                "S3Key": asset_lambda_on_update_game.s3_object_key,
            },
        },
    )


def test_connect_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_connect = Asset(
        lambda_stack,
        "lambda_on_connect",
        path="./../backend/websocket_lambdas/",
    )
    lambda_on_connect = lambda_stack.resolve(
        asset_lambda_on_connect.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "lambda_on_connect.on_connect",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_connect,
                "S3Key": asset_lambda_on_connect.s3_object_key,
            },
        },
    )


def test_authenticate_lambda(app, lambda_stack, template: Template):
    asset_lambda_authenticate = Asset(
        lambda_stack,
        "lambda_authenticate_websocket",
        path="./../backend/websocket_lambdas/",
    )
    lambda_authenticate = lambda_stack.resolve(
        asset_lambda_authenticate.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "lambda_authenticate_websocket.on_connect",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_authenticate,
                "S3Key": asset_lambda_authenticate.s3_object_key,
            },
        },
    )
