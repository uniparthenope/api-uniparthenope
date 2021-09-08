import sys
import traceback

from flask import request, g
from app import api, db
from flask_restplus import Resource
import requests
import base64
from ldap3 import Server, Connection, ALL
from functools import wraps
import hashlib
from datetime import datetime, timedelta

from app.apis.eating.models import UserFood
from app.models import TokenAuth

from app.apis.uniparthenope.demo import users_demo
from app.log.log import time_log
from app.config import Config

from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general, auth_token_required, ldap_auth

import cryptography
from cryptography.fernet import Fernet

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def auth(token):
    headers = {
        'Content-Type': "application/json",
        "Authorization": "Basic " + token
    }

    try:
        token = Fernet(Config.PRIVATE_KEY).decrypt(token.encode()).decode()
        print(token)

        base64_bytes = token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        token_hash = hashlib.md5(base64_bytes).hexdigest()

        authorized = TokenAuth.query.filter_by(token_MD5=token_hash).filter(TokenAuth.expire_time>datetime.now()).first()
        if authorized is not None:
            g.response = eval(authorized.result)
            return eval(authorized.result), 200
        else:
            username = token_string.split(':')[0]
            password = token_string.split(':')[1]

            user = UserFood.query.filter_by(username=username).first()
            if user is not None and user.check_password(password):
                r = {'user': {
                    "nomeBar": user.bar,
                    "nome": user.nome.upper(),
                    "cognome": user.cognome.upper(),
                    "grpDes": user.grpDes,
                    "grpId": user.grpId,
                    "telefono": user.telefono,
                    "sesso": user.sesso,
                    "email": user.email,
                    "userId": username
                    }
                }
                g.response = r
                return r, 200
            else:
                response = requests.request("GET", url + "login", headers=headers, timeout=60)
                if response.status_code == 401:
                    try:
                        r = ldap_auth(username, password)
                        g.response = r

                        if r is not None:
                            x = TokenAuth(token_MD5=token_hash, result=str(r), expire_time = datetime.now() + timedelta(minutes=60))
                            db.session.add(x)
                            db.session.commit()

                            return r, 200
                        else:
                            return {"errMsg": "Invalid Credentials"}, 401
                    except:
                        db.session.rollback()
                        print("Unexpected error:")
                        print("Title: " + sys.exc_info()[0].__name__)
                        print("Description: " + traceback.format_exc())
                        return {"errMsg": "Invalid Credentials"}, 401

                elif response.status_code == 503:
                    return {'errMsg': "Server down!"}, 503

                elif response.status_code == 200:
                    print("ESSE3 success!")
                    r = response.json()
                    if r['credentials']['user'] != r['user']['userId'] and r['credentials']['user'] != r['user']['codFis']:
                            r['user']['userId'] = r['credentials']['user']
                    g.response = r

                    if r['user']['grpDes'] == "Docenti" or r['user']['grpDes'] == "Registrati":
                        return r, 200

                    elif r['user']['grpDes'] == "Studenti" and len(r['user']['trattiCarriera']) == 0:
                        r['user']['grpId'] = 97
                        r['user']['grpDes'] = "Dottorandi"
                        return r, 200

                    else:
                        for i in range(0, len(r['user']['trattiCarriera'])):
                            r["user"]["trattiCarriera"][i]["strutturaDes"] = ""
                            r["user"]["trattiCarriera"][i]["strutturaId"] = ""
                            r["user"]["trattiCarriera"][i]["strutturaGaId"] = ""
                            r["user"]["trattiCarriera"][i]["corsoGaId"] = ""

                        return r, 200

    except requests.exceptions.Timeout as e:
        return {'errMsg': 'Timeout Error!'}, 500

    except requests.exceptions.TooManyRedirects as e:
        return {'errMsg': str(e)}, 500

    except requests.exceptions.RequestException as e:
        return {'errMsg': str(e)}, 500

    except cryptography.fernet.InvalidToken as e:
        return {"errMsg": "Not Authorized!"}, 403


# ------------- LOGIN -------------
class Login_v2(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self):
        """Server Login"""
        print("LOGIN ...")

        token = g.pop('token')

        r = auth(token)

        return r
