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
        "Lambda": {
            "stackName": "LambdaStackDev",
            "lambdas": {
                "lambda_post": {
                    "name": "lambdaDev_post",
                    "code": "./../backend/rest_lambdas/post_lambda",
                    "handler": "post",
                    "runtime": "python3.9",
                },
                "lambda_get": {
                    "name": "lambdaDev_get",
                    "code": "./../backend/rest_lambdas/get_lambda",
                    "handler": "get",
                    "runtime": "python3.9",
                },
                "lambda_put": {
                    "name": "lambdaDev_put",
                    "code": "./../backend/rest_lambdas/put_lambda",
                    "handler": "put",
                    "runtime": "python3.9",
                },
                "lambda_join": {
                    "name": "lambdaDev_join",
                    "code": "./../backend/rest_lambdas/join_lambda",
                    "handler": "lambda_join.join",
                    "runtime": "python3.9",
                },
                "lambda_on_create_game": {
                    "name": "lambdaDev_createGame",
                    "code": "./../backend/websocket_lambdas/lambda_on_create_game",
                    "handler": "lambda_on_create_game.on_create_game",
                    "runtime": "python3.9",
                },
                "lambda_on_join_game": {
                    "name": "lambdaDev_joinGame",
                    "code": "./../backend/websocket_lambdas/lambda_on_join_game",
                    "handler": "lambda_on_join_game.on_join_game",
                    "runtime": "python3.9",
                },
                "lambda_on_update_game": {
                    "name": "lambdaDev_updateGame",
                    "code": "./../backend/websocket_lambdas/lambda_on_update_game",
                    "handler": "lambda_on_update_game.on_update_game",
                    "runtime": "python3.9",
                }
            }
        }
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
    asset_get = Asset(
        lambda_stack, "Lambda-Get", path="./../backend/rest_lambdas/get_lambda/"
    )
    get_name = lambda_stack.resolve(asset_get.s3_bucket_name)

    asset_post = Asset(
        lambda_stack, "Lambda-Post", path="./../backend/rest_lambdas/post_lambda/"
    )
    post_name = lambda_stack.resolve(asset_get.s3_bucket_name)

    asset_put = Asset(
        lambda_stack, "Lambda-Put", path="./../backend/rest_lambdas/put_lambda/"
    )
    put_name = lambda_stack.resolve(asset_get.s3_bucket_name)

    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "get",
            "Runtime": "python3.9",
            "Code": {"S3Bucket": get_name, "S3Key": asset_get.s3_object_key},
        },
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "post",
            "Runtime": "python3.9",
            "Code": {"S3Bucket": post_name, "S3Key": asset_post.s3_object_key},
        },
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "put",
            "Runtime": "python3.9",
            "Code": {"S3Bucket": put_name, "S3Key": asset_put.s3_object_key},
        },
    )
