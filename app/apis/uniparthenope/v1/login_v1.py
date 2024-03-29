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
from app.models import TokenAuth, OtherUser

from app.apis.uniparthenope.demo import users_demo
from app.log.log import time_log
from app.config import Config


url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


# GLOBAL FUNCTIONS
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return {'message': 'Token is missing.'}, 401

        _token = token.split()[1]

        if _token in users_demo:
            g.token = users_demo[_token]
        else:
            g.token = _token

        return f(*args, **kwargs)

    return decorated


def token_required_general(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return {'message': 'Token is missing.'}, 401

        _token = token.split()[1]

        if _token in users_demo:
            g.token = users_demo[_token]
        else:
            g.token = _token

        status = auth(g.token)
        g.status = status[1]

        return f(*args, **kwargs)

    return decorated


def auth_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = None

        if 'Token' in request.headers:
            auth_token = request.headers['Token']

        if not auth_token:
            return {'message': 'Auth Token is missing.'}, 401

        g.auth_token = auth_token

        return f(*args, **kwargs)

    return decorated


@time_log(title="LOGIN_V1", filename="login_v1.log", funcName="ldap_auth")
def ldap_auth(user, passwd):
    # define the server
    s = Server(Config.LDAP_SERVER, get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # the following is the user_dn format provided by the ldap server
    base_dn = ",ou=people,dc=uniparthenope,dc=it"
    user_dn = "uid=" + user + base_dn
    searchAttribute = ["uid","sn","givenname","schacPersonalUniqueID", "employeNumber"]

    # define the connection
    c = Connection(s, user=user_dn, password=passwd)

    # perform the Bind operation
    c.bind()

    if c.result['result'] == 0:
        base_dn_1 = "dc=uniparthenope,dc=it"
        c.search(base_dn_1, '(uid='+ user +')', attributes=['*']) 

        result = c.response

        c.unbind()
    
        for x in result:
            try:
                codFis = x['attributes']['schacPersonalUniqueID'][0]
            except:
                codFis = ""
            nc = x['attributes']['cn'][0]
            _nc = nc.split(" ")
            if len(_nc) < 2:
                return {'user':{'lastName': x['attributes']['sn'][0].upper(), 'firstName': x['attributes']['cn'][0].upper(), 'codFis': codFis, "grpDes": "PTA", "grpId": 99, "userId": x['attributes']['uid'][0]}}
            else:
                return {'user':{'lastName': x['attributes']['cn'][0], 'firstName': "", 'codFis': x['attributes']['schacPersonalUniqueID'][0].upper(), "grpDes": "PTA", "grpId": 99, "userId": x['attributes']['uid'][0]}}

    else:
        c.unbind()
        return None
    

def LDAP(username, password, token_hash):
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


@time_log(title="LOGIN_V1", filename="login_v1.log", funcName="auth")
def auth(token):
    headers = {
        'Content-Type': "application/json",
        "Authorization": "Basic " + token
    }

    try:
        base64_bytes = token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        token_hash = hashlib.md5(base64_bytes).hexdigest()

        try:
            authorized = TokenAuth.query.filter_by(token_MD5=token_hash).filter(TokenAuth.expire_time>datetime.now()).first()
        except:
            authorized = None
        if authorized is not None:
            g.response = eval(authorized.result)
            return eval(authorized.result), 200
        else:
            username = token_string.split(':')[0]
            password = token_string.split(':')[1]

            try:
                user = UserFood.query.filter_by(username=username).first()
            except:
                user = None
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
                try:
                    user = OtherUser.query.filter_by(username=username).first()
                except:
                    user = None
                if user is not None and user.check_password(password):
                    r = {
                        'user': {
                            "userId": username,
                            "grpId": user.grpId,
                            "grpDes": "Guest",
                            "lastName": user.cognome,
                            "firstName": user.nome,
                            "codFis": user.codFis
                        },
                        'authToken': ""
                    }
                    g.response = r
                    return r, 200
                else:
                    response = requests.request("GET", url + "login", headers=headers, timeout=60)
                    if response.status_code == 401:
                        return LDAP(username, password, token_hash)

                    elif response.status_code == 503:
                        return LDAP(username, password, token_hash)
                        #return {'errMsg': "Server down!"}, 503

                    elif response.status_code == 200:
                        #print("ESSE3 success!")
                        r = response.json()
                        if r['credentials']['user'] != r['user']['userId'] and r['credentials']['user'] != r['user']['codFis'] and r['user']['userId'] != r['user']['codFis']:
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
    except:
        print(token)
        print("Unexpected error:")
        print("Title: " + sys.exc_info()[0].__name__)
        print("Description: " + traceback.format_exc())
        return {'errMsg': "Errore generico login"}, 500

# ------------- LOGIN -------------
class Login(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self):
        """Server Login"""
        #print("LOGIN ...")

        token = g.pop('token')

        r = auth(token)

        return r


# ------------- LOGOUT -------------
class Logout(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    @auth_token_required
    def get(self):
        """Server Logout"""
        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "logout/;jsessionid=" + g.pop('auth_token'), headers=headers, timeout=60)

            if response.status_code == 200:
                return {"logout": "ok"}, 200
            else:
                return {"logout": "error"}, 500

        except requests.exceptions.Timeout as e:
            return {'errMsg': str(e)}, 500

        except requests.exceptions.RequestException as e:
            return {'errMsg': str(e)}, 500

        except:
            return {'errMsg': 'generic error'}, 500
