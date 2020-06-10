from app import api

version = "1.0"
ver = "v1"
url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"

ns = api.namespace('Eating', description='Eating App operations')

from app.apis.eating.v1.eating_v1 import newUser, getUsers, getToday

ns.add_resource(newUser, '/v1/newUser', methods=['POST'])
ns.add_resource(getUsers, '/v1/getUsers', methods=['GET'])
ns.add_resource(getToday, '/v1/getToday', methods=['GET'])