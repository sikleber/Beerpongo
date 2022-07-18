import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from stacks.beerpongo_api_gateway_stack import BeerpongoAPIGatewayStack


@pytest.fixture
def app():
    yield App()


@pytest.fixture
def mock_config():
    yield {
        "APIGateway": {
            "stackName": "BeerpongoAPIGatewayStack",
            "apiFile": "./config/api_beerpongo.json",
            "id": "Beerpongo-api",
        }
    }


@pytest.fixture
def apigateway_stack(app, mock_config):
    info = {
        "get_LambdaName": "get_LambdaName",
        "post_LambdaName": "post_LambdaName",
        "put_LambdaName": "put_LambdaName",
        "join_LambdaName": "join_LambdaName",
    }
    yield BeerpongoAPIGatewayStack(
        app,
        construct_id="BeerpongoAPIGatewayStack",
        config=mock_config,
        LambdaInfo=info,
    )


@pytest.fixture
def template(apigateway_stack):
    yield Template.from_stack(apigateway_stack)


def test_beerpongo_api_gateway_stack(
    app, apigateway_stack, template: Template
):
    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {
            "Body": {
                "swagger": "2.0",
                "info": {
                    "description": "API for Beerpongo",
                    "version": "1.0.0",
                    "title": "Beerpongo",
                },
                "tags": [
                    {"name": "Game", "description": "Operations for a game."}
                ],
                "paths": {
                    "/game": {
                        "post": {
                            "tags": ["Game"],
                            "summary": "Create a new game",
                            "description": "Creates a new game.",
                            "operationId": "create game",
                            "produces": ["application/json"],
                            "responses": {
                                "200": {
                                    "description": "New game created.",
                                    "schema": {"$ref": "#/definitions/Game"},
                                },
                                "400": {"description": "Error"},
                            },
                            "x-amazon-apigateway-integration": {
                                "httpMethod": "POST",
                                "uri": "arn:${AWS::Partition}:apigateway"
                                ":${"
                                "AWS::Region}:lambda:path/2015-03"
                                "-31/functions/post_LambdaName"
                                "/invocations",
                                "responses": {
                                    "default": {"statusCode": 200}
                                },
                                "passthroughBehavior": "when_no_match",
                                "contentHandling": "CONVERT_TO_TEXT",
                                "type": "aws",
                            },
                        },
                        "put": {
                            "tags": ["Game"],
                            "summary": "Update an existing game",
                            "description": "",
                            "operationId": "updateGame",
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "parameters": [
                                {
                                    "in": "body",
                                    "name": "body",
                                    "description": "Game-object that needs to be updated.",
                                    "required": True,
                                    "schema": {"$ref": "#/definitions"
                                                       "/GameUpdate"},
                                }
                            ],
                            "responses": {
                                "200": {"description": "Update ok"},
                                "400": {"description": "Invalid ID supplied"},
                                "500": {"description": "Error updating Game state"},
                            },
                            "x-amazon-apigateway-integration": {
                                "httpMethod": "POST",
                                "uri": "arn:${AWS::Partition}:apigateway:${"
                                "AWS::Region}:lambda:path/2015-03-31"
                                "/functions/put_LambdaName/invocations",
                                "responses": {
                                    "default": {
                                        "statusCode": "200"
                                    }
                                },
                                "passthroughBehavior": "when_no_match",
                                "contentHandling": "CONVERT_TO_TEXT",
                                "type": "aws",
                            },
                        }
                    },
                    "/game/{GameId}": {
                        "get": {
                            "tags": ["Game"],
                            "summary": "Get an existing game",
                            "description": "",
                            "produces": ["application/json"],
                            "parameters": [
                                {
                                    "in": "path",
                                    "name": "GameId",
                                    "required": True,
                                    "type": "integer",
                                    "format": "int8",
                                }
                            ],
                            "responses": {
                                "200": {
                                    "description": "Game found",
                                    "schema": {"$ref": "#/definitions/Game"},
                                },
                                "404": {"description": "Game not found"},
                            },
                            "x-amazon-apigateway-integration": {
                                "httpMethod": "POST",
                                "uri": "arn:${AWS::Partition}:apigateway"
                                ":${"
                                "AWS::Region}:lambda:path/2015-03"
                                "-31/functions/get_LambdaName"
                                "/invocations",
                                "responses": {
                                    "default": {"statusCode": 200}
                                },
                                "passthroughBehavior": "when_no_match",
                                "contentHandling": "CONVERT_TO_TEXT",
                                "type": "aws",
                            },
                        }
                    },
                },
                "definitions": {
                    "Game": {
                        "type": "object",
                        "properties": {
                            "GameId": {
                                "type": "integer",
                                "format": "int8",
                                "description": "id of the game",
                            },
                            "State": {
                                "type": "string",
                                "description": "current state of the game in the form \"[ID]:[0-9, X],[ID]:[0-9, X],[ID]:[0-9, X],[ID]:[0-9, X],[ID]:[0-9, X]\"",
                            },
                        },
                    },
                    "GameUpdate": {
                        "type": "object",
                        "properties": {
                            "GameId": {
                                "type": "integer",
                                "format": "int8",
                                "description": "id of the game",
                            },
                            "State": {
                                "type": "string",
                                "description": "[0-9, X]",
                            },
                        },
                    },
                },
            },
            "Name": "Beerpongo-api",
        },
    )
