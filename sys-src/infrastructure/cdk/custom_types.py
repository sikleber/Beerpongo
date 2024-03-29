from typing import TypedDict

from aws_cdk.aws_lambda import IFunction


class NamedIdTypeDict(TypedDict):
    id: str
    name: str


class BaseStackConfig(TypedDict):
    stackName: str


class DynamoDbTableConfig(TypedDict):
    id: str
    tableName: str


class DynamoDbStackConfig(BaseStackConfig):
    table: DynamoDbTableConfig


class LambdaConfig(TypedDict):
    name: str


class LambdaLayerConfig(TypedDict):
    id: str
    pipenvDir: str
    sourcesDir: str


class LambdaStackLambdasConfig(TypedDict):
    lambda_authenticate_websocket: LambdaConfig
    lambda_on_connect: LambdaConfig
    lambda_on_create_game: LambdaConfig
    lambda_on_join_game: LambdaConfig
    lambda_on_join_game_as_guest: LambdaConfig
    lambda_on_update_game: LambdaConfig


class LambdaStackConfig(BaseStackConfig):
    layer: LambdaLayerConfig
    lambdas: LambdaStackLambdasConfig


class CognitoStackConfig(BaseStackConfig):
    userPool: NamedIdTypeDict
    userPoolClient: NamedIdTypeDict


class ApiGatewayWebsocketStackRouteConfig(TypedDict):
    id: str
    responseId: str
    key: str


class ApiGatewayWebsocketStackRoutesConfig(TypedDict):
    createGameRoute: ApiGatewayWebsocketStackRouteConfig
    joinGameRoute: ApiGatewayWebsocketStackRouteConfig
    joinAsGuestGameRoute: ApiGatewayWebsocketStackRouteConfig
    updateGameRoute: ApiGatewayWebsocketStackRouteConfig


class ApiGatewayWebsocketStackConfig(BaseStackConfig):
    id: str
    name: str
    authorizerId: str
    connectRouteIntegrationId: str
    stage: NamedIdTypeDict
    routes: ApiGatewayWebsocketStackRoutesConfig


class CdkConfig(TypedDict):
    configName: str
    region: str
    dynamodbStack: DynamoDbStackConfig
    lambdaStack: LambdaStackConfig
    cognitoStack: CognitoStackConfig
    apiGatewayWebsocketStack: ApiGatewayWebsocketStackConfig


class RouteLambdas(TypedDict):
    createGameRoute: IFunction
    joinGameRoute: IFunction
    joinAsGuestGameRoute: IFunction
    updateGameRoute: IFunction
