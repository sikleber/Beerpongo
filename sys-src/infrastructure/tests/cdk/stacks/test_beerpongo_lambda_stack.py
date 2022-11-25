import pytest
from aws_cdk.assertions import Template, Match
from aws_cdk.aws_s3_assets import Asset

from stacks.beerpongo_lambda_stack import BeerpongoLambdaStack


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
            "Layers": [Match.any_value()]
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
            "Layers": [Match.any_value()]
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
            "Layers": [Match.any_value()]
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
            "Layers": [Match.any_value()]
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
            "Layers": [Match.any_value(), Match.any_value()]
        },
    )
