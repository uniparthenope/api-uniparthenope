import requests

from app import api, Config
from flask_restplus import Resource
from flask import request, g

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('technologyadvising')

from app.apis.technology_advising.v1.auth import token_required_general

# ------------- INFO -------------
parser = api.parser()


@ns.doc(parser=parser)
class getInfo(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, username):
        """get users info"""
        if g.status == 200:
            headers = {
                'Content-Type': "application/json",
                "Authorization": "Basic " + Config.USER_ROOT
            }

            response_prof = requests.request("GET", url + "anagrafica-service-v2/docenti", headers=headers, timeout=5)
            _response_prof = response_prof.json()

            print(_response_prof)
        else:
            return {'errMsg': 'Autenticazione fallita!'}, g.status