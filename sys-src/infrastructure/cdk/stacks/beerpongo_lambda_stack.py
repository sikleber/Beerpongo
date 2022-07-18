import aws_cdk.aws_lambda as lambda_
from aws_cdk import Stack
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement, ServicePrincipal


class BeerpongoLambdaStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read the config

        dynamodb_config = config.get("dynamoDB")
        games_table_config = dynamodb_config.get("gamesTable")
        lambda_config = config.get("Lambda")
        post_config = lambda_config.get("lambdas").get("lambda_post")
        get_config = lambda_config.get("lambdas").get("lambda_get")
        put_config = lambda_config.get("lambdas").get("lambda_put")
        join_config = lambda_config.get("lambdas").get("lambda_join")

        # Create the lambdas
        self.lambda_post = lambda_.Function(
            self,
            id=post_config["name"],
            runtime=lambda_.Runtime(post_config["runtime"]),
            handler=post_config["handler"],
            code=lambda_.Code.from_asset(post_config["code"]),
            environment={ "DB_TABLE" : games_table_config["tableName"]}
        )

        self.lambda_get = lambda_.Function(
            self,
            id=get_config["name"],
            runtime=lambda_.Runtime(get_config["runtime"]),
            handler=get_config["handler"],
            code=lambda_.Code.from_asset(get_config["code"]),
            environment={ "DB_TABLE" : games_table_config["tableName"]}
        )

        self.lambda_put = lambda_.Function(
            self,
            id=put_config["name"],
            runtime=lambda_.Runtime(put_config["runtime"]),
            handler=put_config["handler"],
            code=lambda_.Code.from_asset(put_config["code"]),
            environment={ "DB_TABLE" : games_table_config["tableName"]}
        )

        self.lambda_join = lambda_.Function(
            self,
            id=join_config["name"],
            runtime=lambda_.Runtime(join_config["runtime"]),
            handler=join_config["handler"],
            code=lambda_.Code.from_asset(join_config["code"]),
            environment={ "DB_TABLE" : games_table_config["tableName"]}
        )


        # granting DynamoDB access
        self.lambda_post.add_to_role_policy(PolicyStatement(
            actions=["dynamodb:GetItem", "dynamodb:PutItem"],
            resources=["*"]
        ))

        self.lambda_get.add_to_role_policy(PolicyStatement(
            actions=["dynamodb:GetItem"],
            resources=["*"]
        ))

        self.lambda_put.add_to_role_policy(PolicyStatement(
            actions=["dynamodb:GetItem", "dynamodb:PutItem"],
            resources=["*"]
        ))

        self.lambda_join.add_to_role_policy(PolicyStatement(
            actions=["dynamodb:GetItem", "dynamodb:PutItem"],
            resources=["*"]
        ))


        self.lambda_get.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-get-permission"
        )

        self.lambda_post.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-post-permission"
        )

        self.lambda_put.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-put-permission"
        )

        self.lambda_join.add_permission(
            principal=ServicePrincipal('apigateway.amazonaws.com'),
            action='lambda:InvokeFunction',
            id="apigateway-put-permission"
        )

