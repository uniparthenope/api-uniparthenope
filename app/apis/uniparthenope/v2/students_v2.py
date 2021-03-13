from flask import g, request
from app import api
from flask_restplus import Resource, fields
import requests
import sys
import traceback

from app.apis.uniparthenope.v1.login_v1 import token_required

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


# ------------- MY EXAMS -------------

parser = api.parser()
parser.add_argument('matId', type=str, required=True, help='User matId')


@ns.doc(parser=parser)
class MyExams(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId):
        """My Exams"""

        my_exams = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "libretto-service-v2/libretti/" + matId + "/righe", headers=headers, timeout=10)
            _response = response.json()

            if response.status_code == 200:
                for i in range(len(_response)):
                    if _response[i]['esito']['modValCod'] is None:
                        tipo = 'G'
                    else:
                        tipo = _response[i]['esito']['modValCod']['value']

                    actual_exam = ({
                                'nome': _response[i]['adDes'],
                                'codice': _response[i]['adCod'],
                                'tipo': tipo,
                                'adId': _response[i]['chiaveADContestualizzata']['adId'],
                                'adsceID': _response[i]['adsceId'],
                                'docente': "",
                                'docenteID': "",
                                'semestre': "",
                                'semestreDes': "",
                                'adLogId': "",
                                'domPartCod': "",
                                'status': {
                                    'esito': _response[i]['stato']['value'],
                                    'voto': _response[i]['esito']['voto'],
                                    'lode': _response[i]['esito']['lodeFlg'],
                                    'data': _response[i]['esito']['dataEsa']
                                },
                                'CFU': _response[i]['peso'],
                                'annoId': _response[i]['annoCorso'],
                                'numAppelliPrenotabili': _response[i]['numAppelliPrenotabili'],
                                'tipoInsDes': _response[i]['tipoInsDes'],
                                'tipoInsCod': _response[i]['tipoInsCod'],
                                'tipoEsaDes': _response[i]['tipoEsaDes']
                            })
                    my_exams.append(actual_exam)
                return my_exams, 200

            else:
                return {'errMsg': _response['retErrMsg']}, response.status_code
        except requests.exceptions.HTTPError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': 'Timeout Error!'}, 500
        except requests.exceptions.RequestException as e:
            return {'errMsg': str(e)}, 500
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500
