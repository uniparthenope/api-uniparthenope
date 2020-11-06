from app import api

version = "1.0"
ver = "v1"
url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"

ns = api.namespace('TechnologyAdvising', description='Services for technology advising')

from app.apis.technology_advising.v1.general_v1 import getInfo
from app.apis.technology_advising.v1.auth import Login

ns.add_resource(getInfo, '/v1/getInfo/<username>', methods=['GET'])
ns.add_resource(Login, '/v1/login', methods=['GET'])
