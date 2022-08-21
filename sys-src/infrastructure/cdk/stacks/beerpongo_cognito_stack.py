import aws_cdk.aws_cognito as cognito
from aws_cdk import Stack
from constructs import Construct


class BeerpongoCognitoStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cognito_config = config.get("cognito")
        user_pool = cognito.UserPool(
            self,
            cognito_config["userPool"]["id"],
            user_pool_name=cognito_config["userPool"]["name"],
        )

        user_pool.add_client(
            cognito_config["userPoolClient"]["id"],
            user_pool_client_name=cognito_config["userPoolClient"]["name"],
        )
