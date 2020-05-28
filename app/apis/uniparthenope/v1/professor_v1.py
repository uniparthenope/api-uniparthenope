from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general
from flask import g
from app import api
from flask_restplus import Resource
import requests
from datetime import datetime, timedelta

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- DEPARTMENT INFO -------------
parser = api.parser()
parser.add_argument('docenteId', type=str, required=True, help='User docenteId')


@ns.doc(parser=parser)
class DetInfo(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, docenteId):
        """Get Detailed Prof Information"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "anagrafica-service-v2/docenti/" + docenteId, headers=headers)
            _response = response.json()

            print(_response)

            return {'settCod': _response[0]['settCod'],
                    'ruoloDocCod': _response[0]['ruoloDocCod'],
                    'docenteMatricola': _response[0]['docenteMatricola'],
                    'facCod': _response[0]['facCod'],
                    'facDes': _response[0]['facDes'],
                    'facId': _response[0]['facId']
                    }, 200

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


# ------------- GET SESSION -------------
class getSession(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get Session"""

        if g.status == 200:
            try:
                response = requests.request("GET", url + "calesa-service-v1/sessioni?order=-aaSesId")
                today = (datetime.today() + timedelta(1*365/12))

                if response.status_code is 200:
                    _response = response.json()

                    for i in range(0, len(_response)):

                        inizio = datetime.strptime(_response[i]['dataInizio'], "%d/%m/%Y %H:%M:%S")
                        fine = datetime.strptime(_response[i]['dataFine'], "%d/%m/%Y %H:%M:%S")
                        if inizio <= datetime.today() <= fine:

                            array = ({
                                'aa_curr': str(_response[i]['aaSesId']) + " - " + str(_response[i]['aaSesId']+1),
                                'semId': _response[i]['sesId'],
                                'semDes': _response[i]['des'],
                                'aaId': _response[i]['aaSesId'],
                            })

                            if i > 0:
                                break

                    return array, 200

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
        else:
            return {'errMsg': 'generic error'}, g.status