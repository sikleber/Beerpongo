import logging
import os
from typing import List, Optional, TypedDict, cast

import jwt
from jwt import PyJWKClient
from typing_extensions import Required


class AuthenticationPolicyStatement(TypedDict):
    Action: str
    Effect: str
    Resource: str


class AuthenticationPolicyDocument(TypedDict):
    Version: str
    Statement: List[AuthenticationPolicyStatement]


class AuthenticationResponse(TypedDict, total=False):
    principalId: Required[str]
    policyDocument: AuthenticationPolicyDocument


try:
    region = os.environ["AWS_REGION"]
    userPoolId = os.environ["USER_POOL_ID"]
    url = f"https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json"
    app_client = os.environ["APP_CLIENT_ID"]

    # fetching jwks
    jwks_client = PyJWKClient(url)
except Exception as e:
    logging.error(e)
    raise Exception("Unable to download JWKS")


def generate_policy(
    principal_id: str,
    effect: Optional[str] = None,
    resource: Optional[str] = None,
) -> AuthenticationResponse:
    auth_response = AuthenticationResponse(principalId=principal_id)

    if effect and resource:
        statement_one = AuthenticationPolicyStatement(
            Action='execute-api:Invoke', Effect=effect, Resource=resource
        )
        policy_document = AuthenticationPolicyDocument(
            Version='2012-10-17', Statement=[statement_one]
        )
        auth_response["policyDocument"] = policy_document

    return auth_response


def on_connect(event: dict, context: dict) -> AuthenticationResponse:
    try:
        # fetching access token from event
        token = event["headers"]["Authorization"]

        # check token structure
        if len(token.split(".")) != 3:
            raise Exception("Unauthorized")
    except Exception as e:
        logging.error(e)
        raise Exception("Unauthorized")

    try:
        # get unverified headers
        headers = jwt.get_unverified_header(token)
        # get signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        # validating exp, iat, signature, iss
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=[cast(str, headers.get("alg"))],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": False,
            },
        )
    except jwt.InvalidTokenError as e:
        logging.error(e)
        return generate_policy(
            principal_id=app_client, effect="Deny", resource=event["methodArn"]
        )
    except jwt.DecodeError as e:
        logging.error(e)
        return generate_policy(
            principal_id=app_client, effect="Deny", resource=event["methodArn"]
        )
    except jwt.InvalidSignatureError as e:
        logging.error(e)
        return generate_policy(
            principal_id=app_client, effect="Deny", resource=event["methodArn"]
        )
    except jwt.ExpiredSignatureError as e:
        logging.error(e)
        return generate_policy(
            principal_id=app_client, effect="Deny", resource=event["methodArn"]
        )
    except jwt.InvalidIssuerError as e:
        logging.error(e)
        return generate_policy(
            principal_id=app_client, effect="Deny", resource=event["methodArn"]
        )
    except jwt.InvalidIssuedAtError as e:
        logging.error(e)
        return generate_policy(
            principal_id=app_client, effect="Deny", resource=event["methodArn"]
        )
    except Exception as e:
        logging.error(e)
        raise Exception("Unauthorized")

    try:
        # verifying audience...use data['client_id'] if verifying an access token else data['aud']
        if app_client != data.get("client_id"):
            raise Exception("Unauthorized")
    except Exception as e:
        logging.error(e)
        raise Exception("Unauthorized")

    try:
        # token_use check
        if data.get("token_use") != "access":
            raise Exception("Unauthorized")
    except Exception as e:
        logging.error(e)
        raise Exception("Unauthorized")

    try:
        # scope check
        if "openid" not in cast(str, data.get("scope")).split(" "):
            raise Exception("Unauthorized")
    except Exception as e:
        logging.error(e)
        raise Exception("Unauthorized")

    return generate_policy(
        principal_id=app_client, effect="Allow", resource=event["methodArn"]
    )
