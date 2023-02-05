import pytest
from aws_cdk.assertions import Match, Template
from aws_cdk.aws_s3_assets import Asset
from stacks.lambda_stack import BeerpongoLambdaStack


@pytest.fixture
def lambda_stack(app, mock_config):
    yield BeerpongoLambdaStack(
        app,
        construct_id="BeerpongoLambdaStack",
        lambda_config=mock_config["lambdaStack"],
        environment_variables={"test": "testValue"},
    )


@pytest.fixture
def template(lambda_stack):
    yield Template.from_stack(lambda_stack)


def test_authenticate_lambda(app, lambda_stack, template: Template):
    asset_lambda_authenticate = Asset(
        lambda_stack,
        "lambda_authenticate_websocket",
        path="./../backend/src/",
    )
    lambda_authenticate = lambda_stack.resolve(
        asset_lambda_authenticate.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "websocket_handler.on_authenticate",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_authenticate,
                "S3Key": asset_lambda_authenticate.s3_object_key,
            },
            "Layers": [Match.any_value()],
        },
    )


def test_connect_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_connect = Asset(
        lambda_stack,
        "lambda_on_connect",
        path="./../backend/src/",
    )
    lambda_on_connect = lambda_stack.resolve(
        asset_lambda_on_connect.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "websocket_handler.on_connect",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_connect,
                "S3Key": asset_lambda_on_connect.s3_object_key,
            },
            "Layers": [Match.any_value()],
        },
    )


def test_create_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_create_game = Asset(
        lambda_stack,
        "lambda_on_create_game",
        path="./../backend/src/",
    )
    lambda_on_create_game_name = lambda_stack.resolve(
        asset_lambda_on_create_game.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "websocket_handler.on_create_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_create_game_name,
                "S3Key": asset_lambda_on_create_game.s3_object_key,
            },
            "Layers": [Match.any_value()],
        },
    )


def test_join_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_join_game = Asset(
        lambda_stack,
        "lambda_on_join_game",
        path="./../backend/src/",
    )
    lambda_on_join_game_name = lambda_stack.resolve(
        asset_lambda_on_join_game.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "websocket_handler.on_join_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_join_game_name,
                "S3Key": asset_lambda_on_join_game.s3_object_key,
            },
            "Layers": [Match.any_value()],
        },
    )


def test_join_as_guest_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_join_game_as_guest = Asset(
        lambda_stack,
        "lambda_on_join_game_as_guest",
        path="./../backend/src/",
    )
    lambda_on_join_game_as_guest_name = lambda_stack.resolve(
        asset_lambda_on_join_game_as_guest.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "websocket_handler.on_join_game_as_guest",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_join_game_as_guest_name,
                "S3Key": asset_lambda_on_join_game_as_guest.s3_object_key,
            },
            "Layers": [Match.any_value()],
        },
    )


def test_update_lambda(app, lambda_stack, template: Template):
    asset_lambda_on_update_game = Asset(
        lambda_stack,
        "lambda_on_update_game",
        path="./../backend/src/",
    )
    lambda_on_update_game_name = lambda_stack.resolve(
        asset_lambda_on_update_game.s3_bucket_name
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "websocket_handler.on_update_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_update_game_name,
                "S3Key": asset_lambda_on_update_game.s3_object_key,
            },
            "Layers": [Match.any_value()],
        },
    )
