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
                "tableName": 'BeerpongoDevGamesTable'
            }
        },
        "lambda": {
            "stackName": "LambdaStackDev",
            "lambdas": {
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
        app, construct_id="BeerpongoLambdaStack", config=mock_config
    )


@pytest.fixture
def template(lambda_stack):
    yield Template.from_stack(lambda_stack)


def test_lambda_stack(app, lambda_stack, template: Template):
    # Get the Bucket-names of the lambda-folders
    asset_lambda_on_create_game = Asset(
        lambda_stack,
        "lambda_on_create_game",
        path="./../backend/websocket_lambdas/",
    )
    lambda_on_create_game_name = lambda_stack.resolve(
        asset_lambda_on_create_game.s3_bucket_name
    )

    asset_lambda_on_join_game = Asset(
        lambda_stack,
        "lambda_on_join_game",
        path="./../backend/websocket_lambdas/",
    )
    lambda_on_join_game_name = lambda_stack.resolve(
        asset_lambda_on_join_game.s3_bucket_name
    )

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
            "Handler": "lambda_on_create_game.on_create_game",
            "Runtime": "python3.9",
            "Code": {
                "S3Bucket": lambda_on_create_game_name,
                "S3Key": asset_lambda_on_create_game.s3_object_key,
            },
        },
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
