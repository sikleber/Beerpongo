from aws_cdk.aws_lambda import IFunction
from typing import TypedDict


class NamedIdTypeDict(TypedDict):
    id: str
    name: str


class BaseStackConfig(TypedDict):
    stackName: str


class DynamoDbTableConfig(TypedDict):
    id: str
    tableName: str


class DynamoDbStackConfig(BaseStackConfig):
    gamesTable: DynamoDbTableConfig


class LambdaConfig(TypedDict):
    name: str
    code: str
    handler: str
    runtime: str


class JwtLayerConfig(TypedDict):
    id: str
    code: str


class AuthenticationLambdaConfig(LambdaConfig):
    jwt_layer: JwtLayerConfig


class LambdaLayerConfig(TypedDict):
    id: str
    code: str
    runtime: str


class LambdaStackLambdasConfig(TypedDict):
    lambda_authenticate_websocket: AuthenticationLambdaConfig
    lambda_on_connect: LambdaConfig
    lambda_on_create_game: LambdaConfig
    lambda_on_join_game: LambdaConfig
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
    dynamodbStack: DynamoDbStackConfig
    lambdaStack: LambdaStackConfig
    cognitoStack: CognitoStackConfig
    apiGatewayWebsocketStack: ApiGatewayWebsocketStackConfig


class RouteLambdas(TypedDict):
    createGameRoute: IFunction
    joinGameRoute: IFunction
    updateGameRoute: IFunction
