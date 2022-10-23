import aws_cdk.aws_cognito as cognito
from aws_cdk import Stack, Duration
from constructs import Construct


class BeerpongoCognitoStack(Stack):
    def __init__(
            self, scope: Construct, construct_id: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cognito_config = config.get("cognito")
        self.user_pool = cognito.UserPool(
            self,
            cognito_config["userPool"]["id"],
            user_pool_name=cognito_config["userPool"]["name"],
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True, phone=True),
            sign_in_case_sensitive=False,
            self_sign_up_enabled=True,
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your email for Beerpongo!!!",
                email_body="Thanks for signing up to Beerpongo!\nYour verification link is:\n{##Verify Email##}",
                email_style=cognito.VerificationEmailStyle.LINK
            ),
            email=cognito.UserPoolEmail.with_cognito()
        )

        self.user_pool_client = self.user_pool.add_client(
            cognito_config["userPoolClient"]["id"],
            user_pool_client_name=cognito_config["userPoolClient"]["name"],
            access_token_validity=Duration.hours(3),
            enable_token_revocation=True,
            auth_flows=cognito.AuthFlow(admin_user_password=True, custom=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(implicit_code_grant=True)
            )
        )
