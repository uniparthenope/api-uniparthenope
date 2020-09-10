from app import api

version = "1.0"
ver = "v1"
url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"

ns = api.namespace('Eating', description='Eating App operations')

from app.apis.eating.v1.eating_v1 import newUser, addMenu, getMenuBar, removeMenu, getAllToday, newRisto

ns.add_resource(newUser, '/v1/newUser', methods=['POST'])
ns.add_resource(newRisto, '/v1/newRisto', methods=['POST'])
ns.add_resource(addMenu, '/v1/addMenu', methods=['POST'])
ns.add_resource(getMenuBar, '/v1/getMenuBar', methods=['GET'])
ns.add_resource(getAllToday, '/v1/getAllToday', methods=['GET'])
ns.add_resource(removeMenu, '/v1/removeMenu/<id>', methods=['GET'])