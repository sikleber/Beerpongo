import pytest
from aws_cdk import App
from aws_cdk.assertions import Template, Match

from stacks.beerpongo_cognito_stack import BeerpongoCognitoStack


@pytest.fixture
def app():
    yield App()


@pytest.fixture
def mock_config():
    yield {
        "cognito": {
            "stackName": 'BeerpongoCognitoStack',
            "userPool": {
                "id": 'BeerpongoUserPool',
                "name": 'BeerpongoUserPool'
            },
            "userPoolClient": {
                "id": 'BeerpongoUserPoolClient',
                "name": 'BeerpongoUserPoolClient'
            }
        }
    }


@pytest.fixture
def cognito_stack(app, mock_config):
    yield BeerpongoCognitoStack(
        app, construct_id="BeerpongoCognitoStack", config=mock_config
    )


@pytest.fixture
def template(cognito_stack):
    yield Template.from_stack(cognito_stack)


def test_beerpongo_cognito_user_pool(template: Template):
    template.has_resource_properties(
        "AWS::Cognito::UserPool",
        {
            "UserPoolName": "BeerpongoUserPool",
            "AccountRecoverySetting": {
                "RecoveryMechanisms": [
                    {
                        "Name": "verified_phone_number",
                        "Priority": 1
                    },
                    {
                        "Name": "verified_email",
                        "Priority": 2
                    }
                ]
            },
            "AdminCreateUserConfig": {
                "AllowAdminCreateUserOnly": True
            },
            "EmailVerificationMessage": "The verification code to your new account is {####}",
            "EmailVerificationSubject": "Verify your new account",
            "SmsVerificationMessage": "The verification code to your new account is {####}",
            "VerificationMessageTemplate": {
                "DefaultEmailOption": "CONFIRM_WITH_CODE",
                "EmailMessage": "The verification code to your new account is {####}",
                "EmailSubject": "Verify your new account",
                "SmsMessage": "The verification code to your new account is {####}"
            }
        }
    )


def test_beerpongo_cognito_user_pool_client(template: Template):
    template.has_resource_properties(
        "AWS::Cognito::UserPoolClient",
        {
            "UserPoolId": {
                "Ref": Match.string_like_regexp("BeerpongoUserPool.*")
            },
            "ClientName": "BeerpongoUserPoolClient",
            "AllowedOAuthFlows": [
                "implicit",
                "code"
            ],
            "AllowedOAuthFlowsUserPoolClient": True,
            "AllowedOAuthScopes": [
                "profile",
                "phone",
                "email",
                "openid",
                "aws.cognito.signin.user.admin"
            ],
            "CallbackURLs": [
                "https://example.com"
            ],
            "SupportedIdentityProviders": [
                "COGNITO"
            ]
        },
    )
