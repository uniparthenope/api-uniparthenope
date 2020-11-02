import urllib
from functools import partial

from bs4 import BeautifulSoup
from flask import g, request
from app import api, Config
from flask_restplus import Resource, fields
import requests
from datetime import datetime
import sys
import json
import traceback
from babel.numbers import format_currency
from concurrent.futures import ThreadPoolExecutor

from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- DEPARTMENT INFO -------------
parser = api.parser()
parser.add_argument('stuId', type=str, required=True, help='User stuId')


@ns.doc(parser=parser)
class DepInfo(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, stuId):
        """Get Department Information"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "anagrafica-service-v2/carriere/" + stuId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                # TODO Add search in GA table 'cdsId' and return GA id

                return {'aaId': _response['aaId'],
                        'dataIscr': _response['dataIscr'],
                        'facCod': _response['facCod'],
                        'facCsaCod': _response['facCsaCod'],
                        'facDes': _response['facDes'],
                        'sedeId': _response['sedeId'],
                        'sediDes': _response['sediDes']
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


# ------------- PIANO ID -------------
# TODO DA ELIMINARE???

parser = api.parser()
parser.add_argument('stuId', type=str, required=True, help='User stuId')


@ns.doc(parser=parser)
class GetPianoId(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, stuId):
        """Get Piano ID"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "piani-service-v1/piani/" + stuId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                if len(_response) != 0:
                    pianoId = _response[0]['pianoId']
                else:
                    pianoId = None

                return {'pianoId': pianoId}, 200
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


# ------------- AVERAGE EXAMS -------------
parser = api.parser()
parser.add_argument('matId', type=str, required=True, help='User matId')
parser.add_argument('value', type=str, required=True, help='A/P (average value)')


@ns.doc(parser=parser)
class GetAverage(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId, value):
        """Get average exams"""

        media_trenta = 0
        media_centodieci = 0
        base_trenta = 0
        base_centodieci = 0

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "libretto-service-v1/libretti/" + matId + "/medie",
                                        headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                # TODO Da semplificare il return
                for i in range(0, len(_response)):
                    if _response[i]['tipoMediaCod']['value'] is value:
                        if _response[i]['base'] == 30:
                            base_trenta = 30
                            media_trenta = _response[i]['media']
                        if _response[i]['base'] == 110:
                            base_centodieci = 110
                            media_centodieci = _response[i]['media']

                if media_trenta is None:
                    media_trenta = "0"

                if media_centodieci is None:
                    media_centodieci = "0"

                return {
                           'trenta': media_trenta,
                           'base_trenta': base_trenta,
                           'base_centodieci': base_centodieci,
                           'centodieci': media_centodieci
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


# ------------- TOTAL NUMBER EXAMS -------------
parser = api.parser()
parser.add_argument('matId', type=str, required=True, help='User matId')


@ns.doc(parser=parser)
class GetTotalExams(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId):
        """Get total exams"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "libretto-service-v2/libretti/" + matId + "/stats",
                                        headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                if len(_response) != 0:
                    totAdSuperate = _response['numAdSuperate'] + _response['numAdFrequentate'] + _response['numAdPianificate']
                    output = {
                        'totAdSuperate': totAdSuperate,
                        'numAdSuperate': _response['numAdSuperate'],
                        'cfuPar': _response['umPesoSuperato'],
                        'cfuTot': _response['umPesoPiano']
                    }
                else:
                    output = {
                        'totAdSuperate': "--",
                        'numAdSuperate': "--",
                        'cfuPar': "--",
                        'cfuTot': "--"
                    }

                return output, 200
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


# ------------- EXAMS -------------
# TODO DA ELIMINARE???


parser = api.parser()
parser.add_argument('stuId', type=str, required=True, help='User stuId')
parser.add_argument('pianoId', type=str, required=True, help='User pianoId')


@ns.doc(parser=parser)
class GetExams(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, stuId, pianoId):
        """Get exams"""

        my_exams = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "piani-service-v1/piani/" + stuId + "/" + pianoId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                for i in range(0, len(_response['attivita'])):
                    if _response['attivita'][i]['sceltaFlg'] == 1:
                        actual_exam = {}
                        actual_exam.update({
                            'nome': _response['attivita'][i]['adLibDes'],
                            'codice': _response['attivita'][i]['adLibCod'],
                            'adId': _response['attivita'][i]['chiaveADContestualizzata']['adId'],
                            'CFU': _response['attivita'][i]['peso'],
                            'annoId': _response['attivita'][i]['scePianoId'],
                            'adsceId': _response['attivita'][i]['adsceAttId']
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


# ------------- CHECK EXAMS -------------

parser = api.parser()
parser.add_argument('matId', type=str, required=True, help='User matId')
parser.add_argument('adsceId', type=str, required=True, help='Exam adsceId')


@ns.doc(parser=parser)
class CheckExam(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId, adsceId):
        """Check passed exams"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "libretto-service-v1/libretti/" + matId + "/righe/" + adsceId,
                                        headers=headers, timeout=5)

            if response.status_code == 500:
                return {
                           'stato': "Indefinito",
                           'tipo': "",
                           'data': "",
                           'lode': 0,
                           'voto': "OK",
                           'anno': 0
                       }, 200

            elif response.status_code == 403:
                _response = response.json()
                return _response, 403

            else:
                _response = response.json()

                if len(_response) == 0:
                    return {
                               'stato': "Indefinito",
                               'tipo': "",
                               'data': "",
                               'lode': 0,
                               'voto': "OK",
                           }, 200

                elif _response['statoDes'] == "Superata":
                    return {
                               'stato': _response['statoDes'],
                               'tipo': _response['tipoInsDes'],
                               'data': _response['esito']['dataEsa'].split()[0],
                               'lode': _response['esito']['lodeFlg'],
                               'voto': _response['esito']['voto'],
                               'anno': _response['annoCorso']
                           }, 200
                else:
                    return {
                               'stato': _response['statoDes'],
                               'tipo': _response['tipoInsDes'],
                               'data': _response['esito']['dataEsa'],
                               'lode': _response['esito']['lodeFlg'],
                               'voto': _response['esito']['voto'],
                               'anno': _response['annoCorso']
                           }, 200

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


# ------------- CHECK APPELLO -------------
parser = api.parser()
parser.add_argument('cdsId', type=str, required=True, help='User cdsId')
parser.add_argument('adId', type=str, required=True, help='User adId')


@ns.doc(parser=parser)
class CheckAppello(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, cdsId, adId):
        """Check Appello"""

        my_exams = []
        bad_status = ["C"] # Used to exclude particoular Status

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "calesa-service-v1/appelli/" + cdsId + "/" + adId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                for i in range(0, len(_response)):
                    #if _response[i]['stato'] == "I" or _response[i]['stato'] == "P":
                    if _response[i]['stato'] not in bad_status:
                        #I = Esami futuri non ancora prenotabili
                        #P = Esami prenotabili

                        actual_exam = {}
                        actual_exam.update({
                            'esame': _response[i]['adDes'],
                            'appId': _response[i]['appId'],
                            'stato': _response[i]['stato'],
                            'statoDes': _response[i]['statoDes'],
                            'docente': _response[i]['presidenteCognome'].capitalize(),
                            'docente_completo': _response[i]['presidenteCognome'].capitalize() + " " + _response[i][
                                'presidenteNome'].capitalize(),
                            'numIscritti': _response[i]['numIscritti'],
                            'note': _response[i]['note'],
                            'descrizione': _response[i]['desApp'],
                            'dataFine': _response[i]['dataFineIscr'].split()[0],
                            'dataInizio': _response[i]['dataInizioIscr'].split()[0],
                            'dataEsame': _response[i]['dataInizioApp'].split()[0],
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


# ------------- CHECK PRENOTAZIONI -------------


parser = api.parser()
parser.add_argument('cdsId', type=str, required=True, help='User cdsId')
parser.add_argument('adId', type=str, required=True, help='User adId')
parser.add_argument('appId', type=str, required=True, help='User appId')
parser.add_argument('stuId', type=str, required=True, help='User stuId')


@ns.doc(parser=parser)
class CheckPrenotazione(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, cdsId, adId, appId, stuId):
        """Check prenotazioni"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET",
                                        url + "calesa-service-v1/appelli/" + cdsId + "/" + adId + "/" + appId + "/iscritti/" + stuId,
                                        headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                if _response['esito']['assenteFlg'] != 1:

                    return {
                               'prenotato': True,
                               'data': _response['dataIns']
                           }, 200
                else:
                    return {'prenotato': False}, 200
            else:
                return {'prenotato': False}, 200

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


# ------------- TOTAL RESERVATIONS -------------


parser = api.parser()
parser.add_argument('matId', type=str, required=True, help='User matId')


def fetch_appelli(token, appelli):
    headers = {
        'Content-Type': "application/json",
        "Authorization": "Basic " + token
    }

    response2 = requests.request("GET", url + "calesa-service-v1/appelli/" + str(
        appelli['cdsId']) + "/" + str(appelli['adId']) + "/" + str(appelli['appId']),
                                 headers=headers, timeout=5)
    _response2 = response2.json()

    adId = appelli['adId']
    appId = appelli['appId']

    item = []

    for x in range(0, len(_response2['turni'])):
        if _response2['turni'][x]['appLogId'] == appelli['appLogId']:
            if _response2['stato'] != "C":
                item.append({
                    'adId': adId,
                    'appId': appId,
                    'nomeAppello': _response2['adDes'],
                    'nome_pres': _response2['presidenteNome'],
                    'cognome_pres': _response2['presidenteCognome'],
                    'numIscritti': _response2['numIscritti'],
                    'note': _response2['note'],
                    'statoDes': _response2['statoDes'],
                    'statoEsito': _response2['statoInsEsiti']['value'],
                    'statoVerb': _response2['statoVerb']['value'],
                    'statoPubbl': _response2['statoPubblEsiti']['value'],
                    'tipoApp': _response2['tipoGestAppDes'],
                    'aulaId': _response2['turni'][x]['aulaId'],
                    'edificioId': _response2['turni'][x]['edificioCod'],
                    'edificioDes': _response2['turni'][x]['edificioDes'],
                    'aulaDes': _response2['turni'][x]['aulaDes'],
                    'desApp': _response2['turni'][x]['des'],
                    'dataEsa': _response2['turni'][x]['dataOraEsa']
                })

    return item


@ns.doc(parser=parser)
class getReservations(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId):
        """Get reservations"""

        pool = ThreadPoolExecutor(max_workers=50)

        array = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "calesa-service-v1/prenotazioni/" + matId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                func = partial(fetch_appelli, g.token)
                for res in pool.map(func, _response):
                    info_json = json.loads(json.dumps(res))
                    array += info_json

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


# ------------- GET PROFESSORS -------------
parser = api.parser()
parser.add_argument('aaId', type=str, required=True, help='User stuId')
parser.add_argument('cdsId', type=str, required=True, help='User pianoId')


def fetch_professors(prof):
    headers = {
        'Content-Type': "application/json",
        "Authorization": "Basic " + Config.USER_ROOT
    }

    response_prof = requests.request("GET", url + "anagrafica-service-v2/docenti/" + str(prof['docenteId']), headers=headers, timeout=5)
    _response_prof = response_prof.json()

    if response_prof.status_code == 200:
        try:
            url_pic = (BeautifulSoup(urllib.request.urlopen('https://www.uniparthenope.it/ugov/person/' + str(_response_prof[0]['idAb'])).read(), features="html.parser")).find('div', attrs={'class': 'views-field-field-ugov-foto'}).find('img').attrs['src']
        except urllib.error.HTTPError:
            url_pic = 'https://www.uniparthenope.it/sites/default/files/styles/fototessera__175x200_/public/default_images/ugov_fotopersona.jpg' 

        item = ({
            'docenteNome': _response_prof[0]['docenteNome'],
            'docenteCognome': _response_prof[0]['docenteCognome'],
            'docenteId': _response_prof[0]['docenteId'],
            'docenteMat': _response_prof[0]['docenteMatricola'],
            'corso': prof['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adDes'],
            'adId': prof['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adId'],
            'telefono': _response_prof[0]['cellulare'],
            'email': _response_prof[0]['eMail'],
            'link': _response_prof[0]['hyperlink'],
            'ugov_id': _response_prof[0]['idAb'],
            'biography': _response_prof[0]['noteBiografiche'],
            'url_pic': url_pic,
            'notes': _response_prof[0]['noteDocente'],
            'publications': _response_prof[0]['notePubblicazioni'],
            'curriculum': _response_prof[0]['noteCurriculum'],
            'ruolo': _response_prof[0]['ruoloDocDes'],
            'settore': _response_prof[0]['settDes']
            })

        return item


@ns.doc(parser=parser)
class getProfessors(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, aaId, cdsId):
        """Get professor's list"""
        
        pool = ThreadPoolExecutor(max_workers=50)

        array = []
        array_docenteId = []

        headers = {
            'Content-Type': "application/json",
        }

        if g.status == 200:
            try:
                response = requests.request("GET",
                                            url + "offerta-service-v1/offerte/" + aaId + "/" + cdsId + "/docentiPerUD",
                                            headers=headers, timeout=5)
                _response = response.json()

                if response.status_code == 200:
                    for res in pool.map(fetch_professors, _response):
                        info_json = json.loads(json.dumps(res))
                        if info_json['docenteId'] not in array_docenteId:
                            array_docenteId.append(info_json['docenteId'])
                            array.append(info_json)
                        else:
                            docente = next((item for item in array if item["docenteId"] == info_json['docenteId']), None)
                            docente['corso'] += ", " + info_json['corso']
                    
                    return sorted(array, key=lambda k: k['docenteCognome']), 200

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


# ------------- TAXES -------------


parser = api.parser()
parser.add_argument('persId', type=str, required=True, help='User persId')


@ns.doc(parser=parser)
class Taxes(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, persId):
        """Taxes situation"""

        array = {}
        array_payed = []
        array_to_pay = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "tasse-service-v1/lista-fatture?persId=" + persId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                for i in range(0, len(_response)):
                    if _response[i]['pagatoFlg'] == 0:
                        item = ({
                            'desc': _response[i]['desMav1'],
                            'fattId': _response[i]['fattId'],
                            'importo': format_currency(_response[i]['importoFattura'], 'EUR', locale='it_IT'),
                            'iuv': _response[i]['iuv'],
                            'scadFattura': _response[i]['scadFattura']
                        })
                        array_to_pay.append(item)
                    elif _response[i]['pagatoFlg'] == 1:
                        item = ({
                            'desc': _response[i]['desMav1'],
                            'fattId': _response[i]['fattId'],
                            'importo': format_currency(_response[i]['importoFattura'], 'EUR', locale='it_IT'),
                            'dataPagamento': _response[i]['dataPagamento'],
                            'scadFattura': _response[i]['scadFattura'],
                            'iur': _response[i]['iur'],
                            'nBollettino': _response[i]['nBollettino']
                        })
                        array_payed.append(item)

                print(array_to_pay)
                format = '%d/%m/%Y'  # The format
                if len(array_to_pay) >= 1 and array_to_pay[0]["scadFattura"] == "null":
                    array_to_pay[0]["scadFattura"] = "Non disponibile"
                    array["semaforo"] = "ROSSO"
                else:
                    if len(array_to_pay) >= 1 and datetime.now() < datetime.strptime(array_to_pay[0]["scadFattura"],
                                                                                     format):
                        array["semaforo"] = "GIALLO"
                    elif len(array_to_pay) >= 1 and datetime.now() > datetime.strptime(array_to_pay[0]["scadFattura"],
                                                                                       format):
                        array["semaforo"] = "ROSSO"
                    elif len(array_to_pay) == 0:
                        array["semaforo"] = "VERDE"

                array["payed"] = array_payed
                array["to_pay"] = array_to_pay

                return array, 200
            else:
                return {'errMsg': _response['retErrMsg']}, _response['statusCode']

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


# ------------- BOOK AN EXAM -------------


parser = api.parser()
parser.add_argument('cdsId', type=str, required=True, help='User cdsId')
parser.add_argument('adId', type=str, required=True, help='User adId')
parser.add_argument('appId', type=str, required=True, help='User appId')
body = ns.model("body", {
    "adsceId": fields.Integer(description="adseId", required=True),
    "notaStu": fields.String(description="note", required=True)
})


@ns.doc(parser=parser)
class BookExam(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    @ns.expect(body)
    def post(self, cdsId, adId, appId):
        '''Book an exam'''

        data = request.json

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            if "adsceId" in data and data['adsceId'] is not None:
                response = requests.request("POST",
                                            url + "calesa-service-v1/appelli/" + cdsId + "/" + adId + "/" + appId + "/iscritti",
                                            headers=headers, json=data, timeout=5)
                if response.status_code == 201:
                    return {'message': 'Ok'}, response.status_code
                else:
                    r = response.json()
                    return {'errMsg': r['retErrMsg']}, response.status_code
            else:
                return {'errMsg': 'Error payload'}, 500
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

# ------------- DELETE A BOOKING -------------


parser = api.parser()
parser.add_argument('cdsId', type=str, required=True, help='User cdsId')
parser.add_argument('adId', type=str, required=True, help='User adId')
parser.add_argument('appId', type=str, required=True, help='User appId')
parser.add_argument('stuId', type=str, required=True, help='User stuId')


@ns.doc(parser=parser)
class DeleteReservation(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def delete(self, cdsId, adId, appId, stuId):
        '''Delete a reservation'''

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("DELETE", url + "calesa-service-v1/appelli/" + cdsId + "/" + adId + "/" + appId + "/iscritti/" + stuId, headers=headers, timeout=5)
            print(response.status_code)
            if response.status_code == 200:
                return {'message': 'Ok'}, response.status_code
            else:
                r = response.json()
                return {'errMsg': r['retErrMsg']}, response.status_code
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
