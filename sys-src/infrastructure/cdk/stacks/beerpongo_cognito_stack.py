import aws_cdk.aws_cognito as cognito

from aws_cdk import Stack
from constructs import Construct


class BeerpongoCognitoStack(Stack):
    def __init__(
            self, scope: Construct, construct_id: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        pass
