from flask import request
from app import api
from flask_restplus import Resource
import requests
import base64
from ldap3 import Server, Connection, ALL
from functools import wraps

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('auth')

#LOGIN
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return {'message': 'Token is missing.'}, 401

        token = token.split()[1]

        return auth(token)

        return f(*args, **kwargs)

    return decorated

def ldap_auth(user, passwd):
    # define the server
    s = Server('ldap.uniparthenope.it', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # the following is the user_dn format provided by the ldap server
    user_dn = "uid=" + user + ",ou=people,dc=uniparthenope,dc=it"

    # define the connection
    c = Connection(s, user=user_dn, password=passwd)

    # perform the Bind operation
    c.bind()

    if c.result['result'] == 0:
        print("LDAP people!")
        return c.result
    else:
        # define the server
        s = Server('ldap-studenti.uniparthenope.it', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

        # the following is the user_dn format provided by the ldap server
        user_dn = "uid=" + user + ",ou=studenti,dc=uniparthenope,dc=it"

        # define the connection
        c = Connection(s, user=user_dn, password=passwd)

        # perform the Bind operation
        c.bind()

        print("LDAP studenti!")
        return c.result



def auth(token):
    result = {"status": "fail"}
    code = 401

    headers = {
        'Content-Type': "application/json",
        "Authorization": "Basic " + token
    }

    try:
        response = requests.request("GET", url + "login", headers=headers)
        print(response.status_code)
        if response.status_code == 401:
            try:
                base64_bytes = token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                r = ldap_auth(token_string.split(':')[0], token_string.split(':')[1])
                if r['result'] == 0:
                    # r.update({"token":token_string})
                    # r["user"] = {"userId":token_string.split(':')[0]}
                    # return r
                    result["status"] = "success"
                    code = 200
                else:
                    # return {"errMsg":"Invalid Credentials"}, 401
                    result["errMsg"] = "Invalid Credentials"

            except:
                # return {"errMsg":"Invalid Credentials"}, 401
                result["errMsg"] = "Invalid Credentials"

        elif response.status_code == 503:
            # return {'errMsg': "Server down!"}, 503
            result["errMsg"] = "Server down"
            code = 503

        elif response.status_code == 200:
            # _response = response.json()
            # _response.update({"token":token})
            # return _response, 200
            print("ESSE3 success!")
            result["status"] = "success"
            code = 200

    except requests.exceptions.Timeout as e:
        print(e)
        #return {'errMsg': e}, 500
        result["errMsg"] = e
        code = 500

    except requests.exceptions.TooManyRedirects as e:
        print(e)
        #return {'errMsg': e}, 500
        result["errMsg"] = e
        code = 500

    except requests.exceptions.RequestException as e:
        print(e)
        #return {'errMsg': e}, 500
        result["errMsg"] = e
        code = 500

    return result, code


parser = api.parser()
@ns.doc(parser=parser)
class Login(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self):
        '''Server Login'''
        print("LOGIN ...")

#LOGOUT

parser = api.parser()
@ns.doc()
class Logout(Resource):
    @property
    def get(self):
        ''' Server logout '''
        try:
            headers = request.headers
            print("TOKEN: " + headers['authToken'])

            response = requests.request("GET", url + "logout/;jsessionid=" + headers['authToken'], headers=headers)

            if response.status_code == 200:
                return 200
            else:
                return response.status_code

        except requests.exceptions.Timeout as e:
            print(e)
            return {'errMsg': e}, 500

        except requests.exceptions.RequestException as e:
            print(e)
            return {'errMsg': e}, 500

        except:
            return {'errMsg': 'generic error'}, 500