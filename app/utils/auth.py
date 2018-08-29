import json

from jose import jwt
from os import getenv
from functools import wraps
from urllib.request import urlopen
from flask import request
from werkzeug.exceptions import Unauthorized, BadRequest

DOMAIN = getenv('AUTH0_DOMAIN')
SECRET = getenv('AUTH0_SECRET')
ALGORITHMS = ['RS256']


def get_token():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise Unauthorized(description='Missing Authorization header.')
    auth = auth.split()
    if len(auth) != 2 or auth[0].lower() != 'bearer':
        raise Unauthorized(
            description='Authorization token must match the following format: "Bearer <token>".')

    return auth[1]


def requires_auth(func):
    """Resource is protected by Authorization token
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        token = get_token()
        jsonurl = urlopen(f'{DOMAIN}.well-known/jwks.json')
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                for key_name in ['kty', 'kid', 'use', 'n', 'e']:
                    rsa_key[key_name] = key[key_name]
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=f'{DOMAIN}api/v2/',
                    issuer=DOMAIN
                )
            except jwt.ExpiredSignatureError:
                raise Unauthorized('Token expired.')
            except jwt.JWTClaimsError:
                raise Unauthorized(
                    'Incorrect claims, please check `audience` and `issuer`.')
            except Exception as e:
                raise BadRequest('Invalid Authorization header. ' + str(e))

            # TODO: Set user in request context

            return func(*args, **kwargs)

        raise BadRequest('Unable to find appropriate key.')
    return decorated
