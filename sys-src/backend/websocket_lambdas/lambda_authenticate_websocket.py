def on_connect(event, context):
    return generate_policy(principal_id="user", effect="Allow", resource=event["methodArn"])


def generate_policy(principal_id, effect, resource):
    auth_response = {"principalId": principal_id}

    if effect and resource:
        statement_one = {
            "Action": 'execute-api:Invoke',
            "Effect": effect,
            "Resource": resource
        }
        policy_document = {
            "Version": '2012-10-17',
            "Statement": [statement_one]
        }
        auth_response["policyDocument"] = policy_document

    return auth_response
