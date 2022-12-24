from __future__ import print_function

import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional, TypedDict

import jwt
from jwt.algorithms import RSAAlgorithm
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
    context: Dict


class HttpVerb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    ALL = '*'


def _find_jwk_value(keys: List[dict], kid: str) -> Any:
    for key in keys:
        if key['kid'] == kid:
            return key


def _generate_authentication_policy(
    principal_id: str,
    effect: Optional[str] = None,
    resource: Optional[str] = None,
    context: dict = {},
) -> AuthenticationResponse:
    auth_response = AuthenticationResponse(
        principalId=principal_id, context=context
    )

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
    _region = ''
    _app_client_id = ''
    _keys_url = ''

    def __init__(
        self,
        region: str,
        user_pool_id: str,
        app_client_id: str,
    ):
        self._region = region
        self._app_client_id = app_client_id
        self._keys_url = (
            f"https://cognito-idp.{region}.amazonaws.com/"
            f"{user_pool_id}/.well-known/jwks.json"
        )

    def authenticate(
        self, token: str, method_arn: str
    ) -> AuthenticationResponse:
        with urllib.request.urlopen(self._keys_url) as url:
            response = url.read()
            keys: List[dict] = json.loads(response)['keys']

            try:
                split_jwt_token = token.split(' ')[-1]
                header: dict = jwt.get_unverified_header(split_jwt_token)
                kid: str = header['kid']

                jwk_value = _find_jwk_value(keys, kid)
                public_key = RSAAlgorithm.from_jwk(json.dumps(jwk_value))

                decoded_jwt_token = jwt.decode(
                    split_jwt_token,
                    public_key,
                    algorithms=['RS256'],
                    audience=self._app_client_id,
                )
                principal_id = decoded_jwt_token['cognito:username']

                # add additional key-value pairs associated
                # with the authenticated principal
                # these are made available by APIGW like so:
                # $context.authorizer.<key>
                # additional context is cached
                context = {
                    'username': decoded_jwt_token['cognito:username'],
                    'email': decoded_jwt_token['email'],
                    'email_verified': decoded_jwt_token['email_verified'],
                }

                return _generate_authentication_policy(
                    principal_id=principal_id,
                    effect="Allow",
                    resource=method_arn,
                    context=context,
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
