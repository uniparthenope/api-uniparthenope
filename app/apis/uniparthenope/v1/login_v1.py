from flask import request, g
from app import api
from flask_restplus import Resource
import requests
import base64
from ldap3 import Server, Connection, ALL
from functools import wraps

from app.apis.ga_uniparthenope.models import Building
from app.apis.eating.models import UserFood

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

        g.token = token.split()[1]

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

        g.token = token.split()[1]
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


def ldap_auth(user, passwd):
    # define the server
    s = Server('ldap.uniparthenope.it',
               get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # the following is the user_dn format provided by the ldap server
    user_dn = "uid=" + user + ",ou=people,dc=uniparthenope,dc=it"

    # define the connection
    c = Connection(s, user=user_dn, password=passwd)

    # perform the Bind operation
    c.bind()

    return c.result


def auth(token):
    headers = {
        'Content-Type': "application/json",
        "Authorization": "Basic " + token
    }

    try:
        base64_bytes = token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]
        password = token_string.split(':')[1]

        user = UserFood.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            return {'user': {
                    "nomeBar": user.nome_bar,
                    "grpDes": "Ristoranti"}
                    }, 202
        else:
            response = requests.request("GET", url + "login", headers=headers)
            if response.status_code == 401:
                try:
                    r = ldap_auth(username, password)
                    if r['result'] == 0:
                        return r, 200
                    else:
                        return {"errMsg": "Invalid Credentials"}, 401
                except:
                    return {"errMsg": "Invalid Credentials"}, 401

            elif response.status_code == 503:
                return {'errMsg': "Server down!"}, 503

            elif response.status_code == 200:
                r = response.json()

                if r['user']['grpDes'] == "Docenti":
                    return r, 200

                else:
                    for i in range(0, len(r['user']['trattiCarriera'])):
                        id = Building.query.filter_by(id_corso=r['user']['trattiCarriera'][i]['cdsId']).first()
                        if id is not None:
                            r["user"]["trattiCarriera"][i]["strutturaDes"] = id.struttura_des
                            r["user"]["trattiCarriera"][i]["strutturaId"] = id.struttura_id
                            r["user"]["trattiCarriera"][i]["strutturaGaId"] = id.struttura_ga_id
                            r["user"]["trattiCarriera"][i]["corsoGaId"] = id.corso_ga_id
                        else:
                            r["user"]["trattiCarriera"][i]["strutturaDes"] = ""
                            r["user"]["trattiCarriera"][i]["strutturaId"] = ""
                            r["user"]["trattiCarriera"][i]["strutturaGaId"] = ""
                            r["user"]["trattiCarriera"][i]["corsoGaId"] = ""

                    return r, 200

    except requests.exceptions.Timeout as e:
        print(e)
        return {'errMsg': e}, 500

    except requests.exceptions.TooManyRedirects as e:
        print(e)
        return {'errMsg': e}, 500

    except requests.exceptions.RequestException as e:
        print(e)
        return {'errMsg': e}, 500


# ------------- LOGIN -------------
class Login(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self):
        """Server Login"""
        print("LOGIN ...")

        token = g.pop('token')

        r = auth(token)

        # token_JWT = (jwt.encode({'userId': token, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY']).decode('UTF-8'))

        # r[0]['token_JWT'] = token_JWT

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
            response = requests.request("GET", url + "logout/;jsessionid=" + g.pop('auth_token'), headers=headers)

            if response.status_code == 200:
                return {"logout": "ok"}, 200
            else:
                return {"logout": "error"}, 500

        except requests.exceptions.Timeout as e:
            print(e)
            return {'errMsg': e}, 500

        except requests.exceptions.RequestException as e:
            print(e)
            return {'errMsg': e}, 500

        except:
            return {'errMsg': 'generic error'}, 500
