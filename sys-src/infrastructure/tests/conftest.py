import pytest
from aws_cdk import App
from custom_types import (
    ApiGatewayWebsocketStackConfig,
    ApiGatewayWebsocketStackRouteConfig,
    ApiGatewayWebsocketStackRoutesConfig,
    CdkConfig,
    CognitoStackConfig,
    DynamoDbStackConfig,
    DynamoDbTableConfig,
    LambdaConfig,
    LambdaLayerConfig,
    LambdaStackConfig,
    LambdaStackLambdasConfig,
    NamedIdTypeDict,
)


@pytest.fixture
def app():
    yield App()


@pytest.fixture(scope="module")
def mock_config() -> CdkConfig:
    yield CdkConfig(
        configName="test",
        dynamodbStack=DynamoDbStackConfig(
            stackName='BeerpongoDynamoDbStackTest',
            gamesTable=DynamoDbTableConfig(
                id='BeerpongoTestGamesTable',
                tableName='BeerpongoTestGamesTable',
            ),
        ),
        lambdaStack=LambdaStackConfig(
            stackName="LambdaStackTest",
            layer=LambdaLayerConfig(
                id="backend_lambda_layer",
                code="./../backend/lambda_layers/backend_lambda_layer.zip",
                runtime='python3.9',
            ),
            lambdas=LambdaStackLambdasConfig(
                lambda_authenticate_websocket=LambdaConfig(
                    name="lambdaTest_authenticate_websocket",
                    code="./../backend/src",
                    handler="websocket_handler.on_authenticate",
                    runtime='python3.9',
                ),
                lambda_on_connect=LambdaConfig(
                    name="lambdaTest_connect_websocket",
                    code="./../backend/src",
                    handler="websocket_handler.on_connect",
                    runtime='python3.9',
                ),
                lambda_on_create_game=LambdaConfig(
                    name="lambdaTest_createGame",
                    code="./../backend/src",
                    handler="websocket_handler.on_create_game",
                    runtime="python3.9",
                ),
                lambda_on_join_game=LambdaConfig(
                    name="lambdaTest_joinGame",
                    code="./../backend/src",
                    handler="websocket_handler.on_join_game",
                    runtime="python3.9",
                ),
                lambda_on_update_game=LambdaConfig(
                    name="lambdaTest_updateGame",
                    code="./../backend/src",
                    handler="websocket_handler.on_update_game",
                    runtime="python3.9",
                ),
            ),
        ),
        apiGatewayWebsocketStack=ApiGatewayWebsocketStackConfig(
            stackName="BeerpongoWebsocketStack",
            id="BeerpongoWebsocketStackId",
            name="BeerpongoWebsocketApi",
            authorizerId='CognitoUserTestAuthorizerId',
            connectRouteIntegrationId='ConnectWebsocketIntegrationTest',
            stage=NamedIdTypeDict(
                id='BeerpongoWebsocketStageTest',
                name="test",
            ),
            routes=ApiGatewayWebsocketStackRoutesConfig(
                createGameRoute=ApiGatewayWebsocketStackRouteConfig(
                    id='CreateGameIntegrationTest',
                    responseId='CreateGameIntegrationTest',
                    key='CreateGame',
                ),
                joinGameRoute=ApiGatewayWebsocketStackRouteConfig(
                    id='JoinGameIntegrationTest',
                    responseId='JoinGameIntegrationTest',
                    key='JoinGame',
                ),
                updateGameRoute=ApiGatewayWebsocketStackRouteConfig(
                    id='UpdateGameIntegrationTest',
                    responseId='UpdateGameIntegrationTest',
                    key='UpdateGame',
                ),
            ),
        ),
        cognitoStack=CognitoStackConfig(
            stackName='BeerpongoCognitoStack',
            userPool=NamedIdTypeDict(
                id='BeerpongoUserPool',
                name='BeerpongoUserPool',
            ),
            userPoolClient=NamedIdTypeDict(
                id='BeerpongoUserPoolClient',
                name='BeerpongoUserPoolClient',
            ),
        ),
    )
