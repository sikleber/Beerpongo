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
        region="eu-central-1",
        dynamodbStack=DynamoDbStackConfig(
            stackName='BeerpongoDynamoDbStackTest',
            table=DynamoDbTableConfig(
                id='BeerpongoTestTable',
                tableName='BeerpongoTestTable',
            ),
        ),
        lambdaStack=LambdaStackConfig(
            stackName="LambdaStackTest",
            layer=LambdaLayerConfig(
                id="backend_lambda_layer",
                pipenvDir="./../backend",
                sourcesDir="./../backend/layer",
            ),
            lambdas=LambdaStackLambdasConfig(
                lambda_authenticate_websocket=LambdaConfig(
                    name="lambdaTest_authenticate_websocket",
                ),
                lambda_on_connect=LambdaConfig(
                    name="lambdaTest_connect_websocket",
                ),
                lambda_on_create_game=LambdaConfig(
                    name="lambdaTest_createGame",
                ),
                lambda_on_join_game=LambdaConfig(
                    name="lambdaTest_joinGame",
                ),
                lambda_on_join_game_as_guest=LambdaConfig(
                    name="lambdaTest_joinGameAsGuest",
                ),
                lambda_on_update_game=LambdaConfig(
                    name="lambdaTest_updateGame",
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
                joinAsGuestGameRoute=ApiGatewayWebsocketStackRouteConfig(
                    id='JoinAsGuestGameIntegrationTest',
                    responseId='JoinAsGuestGameIntegrationTest',
                    key='JoinAsGuestGame',
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
