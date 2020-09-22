from flask import g, request
from app import api
from flask_restplus import Resource, fields
import requests
from datetime import datetime, timedelta
import base64
import json
import sys
import traceback
import urllib
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from babel.numbers import format_currency
import unicodedata

from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general

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
            response = requests.request("GET", url + "libretto-service-v2/libretti/" + matId + "/partizioni",
                                         headers=headers)
            _response = response.json()

            if response.status_code == 200:
                response2 = requests.request("GET", url + "libretto-service-v2/libretti/" + matId + "/righe",
                                            headers=headers)

                _response2 = response2.json()

                if response2.status_code == 200:
                    for i in range(len(_response)):
                        x = next(item for item in _response2 if item["adsceId"] == _response[i]['adsceId'])
                        actual_exam = ({
                            'nome': _response[i]['chiaveAdContestualizzata']['adDes'],
                            'codice': _response[i]['chiaveAdContestualizzata']['adCod'],
                            'adId': _response[i]['chiaveAdContestualizzata']['adId'],
                            'adsceID': _response[i]['adsceId'],
                            'docente': _response[i]['cognomeDocTit'] + " " + _response[i]['nomeDoctit'],
                            'docenteID': _response[i]['docenteId'],
                            'semestre': _response[i]['partEffCod'],
                            'semestreDes': _response[i]['partEffDes'],
                            'adLogId': _response[i]['chiavePartizione']['adLogId'],
                            'domPartCod': _response[i]['chiavePartizione']['domPartCod'],
                            'status': {
                                'esito': x['stato']['value'],
                                'voto': x['esito']['voto'],
                                'lode': x['esito']['lodeFlg'],
                                'data': x['esito']['dataEsa']
                            },
                            'CFU': x['peso'],
                            'annoId': x['annoCorso'],
                            'numAppelliPrenotabili': x['numAppelliPrenotabili'],
                            'tipoInsDes': x['tipoInsDes'],
                            'tipoInsCod': x['tipoInsCod'],
                            'tipoEsaDes': x['tipoEsaDes']
                        })
                        my_exams.append(actual_exam)

                    return my_exams, 200
                else:
                    return {'errMsg': _response2['retErrMsg']}, response2.status_code

            else:
                return {'errMsg': _response['retErrMsg']}, response.status_code
        except requests.exceptions.HTTPError as e:
            return {'errMsg': e}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': e}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': e}, 500
        except requests.exceptions.RequestException as e:
            return {'errMsg': e}, 500
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500