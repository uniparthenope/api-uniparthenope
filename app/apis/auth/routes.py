from app import api

version = "1.0"
ver = "v1"
url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"

ns = api.namespace('auth', description='Authorization operations')

##-----------------LOGIN------------------##
from app.apis.auth.v1.auth_v1 import Login, Logout

ns.add_resource(Login, '/v1/login', methods=['GET'])
ns.add_resource(Logout, '/v1/logout', methods=['GET'])