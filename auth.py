import boto3
import hmac
import hashlib
import base64
import jwt
import re

from logger import logger

cognito_client = boto3.client('cognito-idp', region_name='ap-southeast-1')

def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(
        str(client_secret).encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()


def login(username, password, app_client_id, app_client_secret):
    try:
        secret_hash = get_secret_hash(username, app_client_id, app_client_secret)

        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            },
            ClientId=app_client_id
        )
        
        if not response or response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception('User is not found!')
        return response


    except cognito_client.exceptions.NotAuthorizedException as e:
        raise Exception(f"User is not verifed.")
    except cognito_client.exceptions.UserNotConfirmedException as e:
        raise Exception("User is not confirmed.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def sign_up(email, password, name, app_client_id, secret_hash):
    try:
        response = cognito_client.sign_up(
                ClientId=app_client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'name',
                        'Value': name
                    }
                ],
                SecretHash=secret_hash
                )
        logger.info(response)
        session = response['Session']
        return session
    except cognito_client.exceptions.UsernameExistsException:
        raise Exception("[ERROR]: Username already exists.")
    except Exception as e:
        raise Exception("[ERROR] An error occurred during sign-up:", e)

def confirm_user_sign_up(username, app_client_id, secret_hash, confirmation_code):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=app_client_id,
            SecretHash=secret_hash,
            Username=username,
            ConfirmationCode=confirmation_code,
            ForceAliasCreation=False,
        )
        return response
    except Exception as e:
        raise Exception(f"[ERROR]: An error occurred during confirm sign-up: {e}")
    
def validate_email_address(email, email_domain):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    if email.split('@')[1] not in email_domain:
        raise Exception("Email domain is not in valid domain!")
    return True

def resend_confirmation_code(app_client_id, secret_hash, username):
    try:
        response = cognito_client.resend_confirmation_code(
            ClientId=app_client_id,
            SecretHash=secret_hash,
            Username=username
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise
        return response
    except:
        raise Exception('Resends the code that confirms a new account failed!!!')

def response_to_auth_challenge(app_client_id, challeng_name, session, challenge_response):
    try:
        response = cognito_client.respond_to_auth_challenge(
            ClientId=app_client_id,
            ChallengeName=challeng_name,
            Session=session,
            ChallengeResponses=challenge_response,
        )
        return response
    except Exception as e:
        raise Exception(f'RespondToAuthChallenge requested failed!!! {e}')
    
