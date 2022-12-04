import logging
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


def _generate_authentication_policy(
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


class CognitoJwtAuthenticationService:
    def __init__(self, region: str, user_pool_id: str, app_client_id: str):
        self._app_client_id = app_client_id
        url = (
            f"https://cognito-idp.{region}.amazonaws.com/"
            f"{user_pool_id}/.well-known/jwks.json"
        )

        try:
            self._jwks_client = PyJWKClient(url)
        except Exception as e:
            logging.error(e)
            raise Exception("Unable to download JWKS")

    def authenticate(
        self, token: str, method_arn: str
    ) -> AuthenticationResponse:
        try:
            # check token structure
            if len(token.split(".")) != 3:
                raise Exception("Invalid token structure")
            # get unverified headers
            headers = jwt.get_unverified_header(token)
            # get signing key
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
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
            return _generate_authentication_policy(
                principal_id=self._app_client_id,
                effect="Deny",
                resource=method_arn,
            )
        except Exception as e:
            logging.error(e)
            raise Exception("Unauthorized")

        try:
            # verifying audience, use data['client_id'] else data['aud']
            if self._app_client_id != data.get("client_id"):
                raise Exception("Token client id does not equal app client id")
            # token_use check
            if data.get("token_use") != "access":
                raise Exception("Token use does not equal \"access\"")
            # scope check
            if "openid" not in cast(str, data.get("scope")).split(" "):
                raise Exception("\"openid\" not found in token scope")
        except Exception as e:
            logging.error(e)
            raise Exception("Unauthorized")

        return _generate_authentication_policy(
            principal_id=self._app_client_id,
            effect="Allow",
            resource=method_arn,
        )
