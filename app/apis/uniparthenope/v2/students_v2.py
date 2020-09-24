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
            print(_response)

            if response.status_code == 200:
                response2 = requests.request("GET", url + "libretto-service-v2/libretti/" + matId + "/righe",
                                            headers=headers)

                _response2 = response2.json()
                print(_response2)

                if response2.status_code == 200:
                    for i in range(len(_response2)):
                        if _response2[i]['esito']['modValCod'] is None:
                            tipo = 'G'
                        else:
                            tipo = _response2[i]['esito']['modValCod']['value']

                        if tipo == 'G':
                            actual_exam = ({
                                'nome': _response2[i]['adDes'],
                                'codice': _response2[i]['adDes'],
                                'tipo': tipo,
                                'adId': _response2[i]['chiaveADContestualizzata']['adId'],
                                'adsceID': _response2[i]['adsceId'],
                                'docente': "",
                                'docenteID': "",
                                'semestre': "",
                                'semestreDes': "",
                                'adLogId': "",
                                'domPartCod': "",
                                'status': {
                                    'esito': _response2[i]['stato']['value'],
                                    'voto': _response2[i]['esito']['voto'],
                                    'lode': _response2[i]['esito']['lodeFlg'],
                                    'data': _response2[i]['esito']['dataEsa']
                                },
                                'CFU': _response2[i]['peso'],
                                'annoId': _response2[i]['annoCorso'],
                                'numAppelliPrenotabili': _response2[i]['numAppelliPrenotabili'],
                                'tipoInsDes': _response2[i]['tipoInsDes'],
                                'tipoInsCod': _response2[i]['tipoInsCod'],
                                'tipoEsaDes': _response2[i]['tipoEsaDes']
                            })
                            my_exams.append(actual_exam)
                        for j in range(len(_response)):
                            if _response2[i]["adsceId"] == _response[j]["adsceId"]:
                                actual_exam = ({
                                    'nome': _response[j]['chiaveAdContestualizzata']['adDes'],
                                    'codice': _response[j]['chiaveAdContestualizzata']['adCod'],
                                    'tipo': tipo,
                                    'adId': _response[j]['chiaveAdContestualizzata']['adId'],
                                    'adsceID': _response[j]['adsceId'],
                                    'docente': _response[j]['cognomeDocTit'] + " " + _response[j]['nomeDoctit'],
                                    'docenteID': _response[j]['docenteId'],
                                    'semestre': _response[j]['partEffCod'],
                                    'semestreDes': _response[j]['partEffDes'],
                                    'adLogId': _response[j]['chiavePartizione']['adLogId'],
                                    'domPartCod': _response[j]['chiavePartizione']['domPartCod'],
                                    'status': {
                                        'esito': _response2[i]['stato']['value'],
                                        'voto': _response2[i]['esito']['voto'],
                                        'lode': _response2[i]['esito']['lodeFlg'],
                                        'data': _response2[i]['esito']['dataEsa']
                                    },
                                    'CFU': _response2[i]['peso'],
                                    'annoId': _response2[i]['annoCorso'],
                                    'numAppelliPrenotabili': _response2[i]['numAppelliPrenotabili'],
                                    'tipoInsDes': _response2[i]['tipoInsDes'],
                                    'tipoInsCod': _response2[i]['tipoInsCod'],
                                    'tipoEsaDes': _response2[i]['tipoEsaDes']
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
