import sys
import traceback

from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general
from flask import g
from app import api, Config
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
            response = requests.request("GET", url + "anagrafica-service-v2/docenti/" + docenteId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                return {'settCod': _response[0]['settCod'],
                        'ruoloDocCod': _response[0]['ruoloDocCod'],
                        'docenteMatricola': _response[0]['docenteMatricola'],
                        'facCod': _response[0]['facCod'],
                        'facDes': _response[0]['facDes'],
                        'facId': _response[0]['facId']
                        }, 200
            else:
                return {'errMsg': _response['retErrMsg']}, response.status_code
        except requests.exceptions.HTTPError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': str(e)}, 500
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


# ------------- GET COURSES -------------
parser = api.parser()
parser.add_argument('aaId', type=str, required=True, help='User aaId')


@ns.doc(parser=parser)
class getCourses(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, aaId):
        """Get Courses"""

        array = []
        array_adId = []

        if g.status == 200:
            if g.response['user']['grpId'] == 7:
                try:
                    headers = {
                        'Content-Type': "application/json",
                        "Authorization": "Basic " + Config.USER_ROOT
                    }

                    response = requests.request("GET", url + "logistica-service-v1/logisticaPerDocente?docenteId=" + str(g.response['user']['docenteId']) + "&" + "aaOffId=" + str(aaId), headers=headers, timeout=10)
                    _response = response.json()
                    #print(_response)

                    if response.status_code == 200:
                        for i in range(len(_response)):
                            if _response[i]['adId'] not in array_adId:
                                array_adId.append(_response[i]['adId'])
                                response2 = requests.request("GET", url + "logistica-service-v1/logistica?aaOffId=" + aaId + "&adId=" + str(_response[i]['adId']), headers=headers, timeout=10)
                                if response2.status_code == 200:
                                    _response2 = response2.json()
                                    if len(_response2) != 0:
                                        inizio = _response2[0]['dataInizio'].split()[0]
                                        fine = _response2[0]['dataFine'].split()[0]
                                        ultMod = _response2[0]['dataModLog'].split()[0]
                                        sede = _response2[0]['sedeDes']
                                    else:
                                        inizio = ""
                                        fine = ""
                                        ultMod = ""
                                        sede = ""

                                    array.append({
                                        'adDes': _response[i]['adDes'],
                                        'adId': _response[i]['adId'],
                                        'cdsDes': _response[i]['cdsDes'],
                                        'cdsId': _response[i]['cdsId'],
                                        'adDefAppCod': _response[i]['adCod'],
                                        'cfu': 'N/A',
                                        'durata': int(_response[i]['ore']),
                                        'obbligatoria': 'N/A',
                                        'libera': 'N/A',
                                        'tipo': 'N/A',
                                        'settCod': _response[i]['settCod'],
                                        'semCod': _response[i]['partCod'],
                                        'semDes': _response[i]['partDes'],
                                        'inizio': inizio,
                                        'fine': fine,
                                        'ultMod': ultMod,
                                        'sede': sede,
                                        'adLogId': _response[i]['adLogId']
                                    })
                        return sorted(array, key=lambda k: k['adDes']), 200
                    else:
                        return {'errMsg': _response['retErrMsg']}, response.status_code

                except requests.exceptions.HTTPError as e:
                    return {'errMsg': str(e)}, 500
                except requests.exceptions.ConnectionError as e:
                    return {'errMsg': str(e)}, 500
                except requests.exceptions.Timeout as e:
                    return {'errMsg': str(e)}, 500
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
            else:
                return {'errMsg': 'Tipo di utente non abilitato!'}, 403
        else:
            return {'errMsg': 'Autenticazione fallita!'}, g.status


# ------------- GET SESSION -------------
class getSession(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get Session"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        if g.status == 200:
            try:
                response = requests.request("GET", url + "calesa-service-v1/sessioni?order=-aaSesId", timeout=5)
                _response = response.json()
                # today = (datetime.today() + timedelta(1 * 365 / 12))

                if response.status_code == 200:
                    for i in range(0, len(_response)):

                        inizio = datetime.strptime(_response[i]['dataInizio'], "%d/%m/%Y %H:%M:%S")
                        fine = datetime.strptime(_response[i]['dataFine'], "%d/%m/%Y %H:%M:%S")


                        response_aa = requests.request("GET",
                                                       url + "servizi-service-v1/annoRif/DR_OFF", headers=headers)
                        _response_aa = response_aa.json()
                        aa = str(_response_aa['aaId'])

                        if response_aa.status_code == 200:

                            if inizio <= datetime.today() <= fine:

                                array = ({
                                    'aa_curr': aa + " - " + str(int(aa) + 1),
                                    'semId': _response[i]['sesId'],
                                    'semDes': _response[i]['des'],
                                    'aaId':  aa,
                                })

                                if i > 0:
                                    break
                        else:
                            return {'errMsg': _response_aa['retErrMsg']}, response_aa.status_code

                    return array, 200
                else:
                    return {'errMsg': _response['retErrMsg']}, response.status_code

            except requests.exceptions.HTTPError as e:
                return {'errMsg': str(e)}, 500
            except requests.exceptions.ConnectionError as e:
                return {'errMsg': str(e)}, 500
            except requests.exceptions.Timeout as e:
                return {'errMsg': str(e)}, 500
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
        else:
            return {'errMsg': 'Autenticazione fallita!'}, g.status


# ------------- GET EXAMS STUDENTS LIST -------------


parser = api.parser()
parser.add_argument('cdsId', type=str, required=True, help='Exam cdsId')
parser.add_argument('adId', type=str, required=True, help='Exam aaId')
parser.add_argument('appId', type=str, required=True, help='Exam appId')


@ns.doc(parser=parser)
class getStudentList(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, cdsId, adId, appId):
        """Get Courses"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        array = []

        try:
            response = requests.request("GET", url + "calesa-service-v1/appelli/" + cdsId +"/" + adId + "/" + appId + "/iscritti",
                                        headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                for i in range(len(_response)):
                    array.append({
                        "adregId": _response[i]['adregId'],
                        "adsceId": _response[i]['adsceId'],
                        "codFisStudente": _response[i]['codFisStudente'],
                        "cognomeStudente": _response[i]['cognomeStudente'],
                        "matricola": _response[i]['matricola'],
                        "nomeStudente": _response[i]['nomeStudente'],
                        "stuId": _response[i]['stuId'],
                        "userId": _response[i]['userId']
                    })
                return array, 200
            else:
                return {'errMsg': _response['retErrMsg']}, response.status_code

        except requests.exceptions.HTTPError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': str(e)}, 500
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
