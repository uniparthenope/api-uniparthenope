from app.apis.uniparthenope.v1.login_v1 import token_required
from flask import g
from app import api
from flask_restplus import Resource
import requests

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- GET COURSES -------------
parser = api.parser()
parser.add_argument('aaId', type=str, required=True, help='User aaId')


@ns.doc(parser=parser)
class getCourses(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, aaId):
        """Get Courses"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        array = []

        try:
            response = requests.request("GET", url + "calesa-service-v1/abilitazioni", headers=headers)

            if response.status_code is 200:
                _response = response.json()
                for x in range(0, len(_response)):
                    if _response[x]['aaAbilDocId'] == int(aaId):
                        response2 = requests.request("GET", url + "offerta-service-v1/offerte/" + aaId + "/" + str(_response[x]['cdsId']) + "/segmenti?adId=" + str(_response[x]['adId']) + "&order=-aaOrdId", headers=headers)
                        if response2.status_code is 200:
                            _response2 = response2.json()
                            response3 = requests.request("GET", url + "logistica-service-v1/logistica?aaOffId=" + aaId + "&adId=" + str(_response[x]['adId']), headers=headers)
                            if response3.status_code is 200:
                                _response3 = response3.json()

                                item = ({
                                    'adDes': _response3[0]['chiaveADFisica']['adDes'],
                                    'adId': _response[x]['adId'],
                                    'cdsDes': _response3[0]['chiaveADFisica']['cdsDes'],
                                    'cdsId': _response[x]['cdsId'],
                                    'adDefAppCod': _response[x]['adDefAppCod'],
                                    'cfu': _response2[0]['peso'],
                                    'durata': _response2[0]['durUniVal'],
                                    'obbligatoria': _response2[0]['freqObbligFlg'],
                                    'libera': _response2[0]['liberaOdFlg'],
                                    'tipo': _response2[0]['tipoAfCod']['value'],
                                    'settCod': _response2[0]['settCod'],
                                    'semCod': _response3[0]['chiavePartizione']['partCod'],
                                    'semDes': _response3[0]['chiavePartizione']['partDes'],
                                    'inizio': _response3[0]['dataInizio'].split()[0],
                                    'fine': _response3[0]['dataFine'].split()[0],
                                    'ultMod': _response3[0]['dataModLog'].split()[0],
                                    'sede': _response3[0]['sedeDes']
                                })
                                array.append(item)
                return array
            else:
                return {'errMsg': 'generic error'}, 500

        except requests.exceptions.HTTPError as e:
            return {'errMsg': e}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': e}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': e}, 500
        except requests.exceptions.RequestException as e:
            return {'errMsg': e}, 500
        except:
            return {'errMsg': 'generic error'}, 500
