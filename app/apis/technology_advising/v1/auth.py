import base64

from app import api, Config
from flask_restplus import Resource
from functools import wraps
from flask import request, g

from app.models import OtherUser

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('technologyAdvising')


def token_required_general(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return {'message': 'Token is missing.'}, 401

        _token = token.split()[1]

        g.response = auth(_token)
        g.status = g.response[1]

        return f(*args, **kwargs)

    return decorated


def auth(token):
    base64_bytes = token.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    token_string = message_bytes.decode('utf-8')

    username = token_string.split(':')[0]
    password = token_string.split(':')[1]

    user = OtherUser.query.filter_by(username=username).first()
    if user is not None and user.check_password(password):
        return {"status": "OK"}, 200
    else:
        return {"errMsg": "Invalid Credentials"}, 401


# ------------- LOGIN -------------
class Login(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Server Login"""
        print("LOGIN ...")

        return g.response