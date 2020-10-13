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
                if len(_response) is not 0:
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
                        'totAdSuperate': "N/A",
                        'numAdSuperate': "N/A",
                        'cfuPar': "N/A",
                        'cfuTot': "N/A"
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


@ns.doc(parser=parser)
class getReservations(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId):
        """Get reservations"""

        array = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "calesa-service-v1/prenotazioni/" + matId, headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                for i in range(0, len(_response)):
                    response2 = requests.request("GET", url + "calesa-service-v1/appelli/" + str(
                        _response[i]['cdsId']) + "/" + str(_response[i]['adId']) + "/" + str(_response[i]['appId']),
                                                 headers=headers, timeout=5)
                    _response2 = response2.json()

                    adId = _response[i]['adId']
                    appId = _response[i]['appId']

                    for x in range(0, len(_response2['turni'])):
                        if _response2['turni'][x]['appLogId'] == _response[i]['appLogId']:
                            if _response2['stato'] is not "C":
                                item = ({
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
                                array.append(item)

                return array
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


def fetch(_response):
    _nome = _response['docenteCognome'] + "%20" + _response['docenteNome']
    nome = _nome.replace(" ", "+")
    url = 'https://www.uniparthenope.it/rubrica?nome_esteso_1=' + nome
    response = urllib.request.urlopen(url)
    webContent = response.read()

    parsed = BeautifulSoup(webContent, 'html.parser')

    div = parsed.find('div', attrs={'class': 'region region-content'})

    ul = div.find('ul', attrs={'class': 'rubrica-list'})
    if ul is not None:
        tel = ul.find('div', attrs={'class': 'views-field views-field-contatto-tfu'})
        if tel is not None:
            tel_f = tel.find('span', attrs={'class': 'field-content'})
            tel_finale = tel_f.text
        else:
            tel_finale = "--"

        email = ul.find('div', attrs={'class': 'views-field views-field-contatto-email'})
        email_finale = email.find('span', attrs={'class': 'field-content'})

        scheda = ul.find('div', attrs={'class': 'views-field views-field-view-uelement'})
        scheda_finale = scheda.find('span', attrs={'class': 'field-content'})

        for a in scheda_finale.find_all('a', href=True):
            link = a['href']

        link_pers = str(link).split("/")[-1]

        response = urllib.request.urlopen(link)
        webContent = response.read()

        parsed = BeautifulSoup(webContent, 'html.parser')
        div = parsed.find('div', attrs={'class': 'views-field views-field-field-ugov-foto'})
        img = div.find('img', attrs={'class': 'img-responsive'})

        prof = ({
            'docenteNome': _response['docenteNome'],
            'docenteCognome': _response['docenteCognome'],
            'docenteId': _response['docenteId'],
            'docenteMat': _response['docenteMatricola'],
            'corso': _response['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adDes'],
            'adId': _response['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adId'],
            'telefono': str(tel_finale),
            'email': str(email_finale.text.rstrip()),
            'link': str(link),
            'ugov_id': link_pers,
            'url_pic': str(img['src'])
        })
    else:
        prof = ({
            'docenteNome': _response['docenteNome'],
            'docenteCognome': _response['docenteCognome'],
            'docenteId': _response['docenteId'],
            'docenteMat': _response['docenteMatricola'],
            'corso': _response['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adDes'],
            'adId': _response['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adId'],
            'telefono': "",
            'email': "",
            'link': "",
            'ugov_id': "",
            'url_pic': "https://www.uniparthenope.it/sites/default/files/styles/fototessera__175x200_/public/default_images/ugov_fotopersona.jpg"
        })

    return prof, 200


@ns.doc(parser=parser)
class getProfessors(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, aaId, cdsId):
        """Get professor's list"""

        pool = ThreadPoolExecutor(max_workers=50)

        headers = {
            'Content-Type': "application/json",
        }

        array = []

        if g.status == 200:
            try:
                response = requests.request("GET",
                                            url + "offerta-service-v1/offerte/" + aaId + "/" + cdsId + "/docentiPerUD",
                                            headers=headers, timeout=5)
                _response = response.json()

                arr_id = []
                temp_prof = []

                if response.status_code == 200:
                    for i in range(len(_response)):
                        if _response[i]['docenteId'] not in arr_id:
                            arr_id.append(_response[i]['docenteId'])
                            temp_prof.append(_response[i])

                    for res in pool.map(fetch, temp_prof):
                        info_json = json.loads(json.dumps(res))[0]
                        info_img = info_json['url_pic']
                        img = base64.b64encode(requests.get(info_img, verify=False).content)

                        item = ({
                            'docenteNome': info_json['docenteNome'],
                            'docenteCognome': info_json['docenteCognome'],
                            'docenteId': info_json['docenteId'],
                            'docenteMat': info_json['docenteMat'],
                            'corso': info_json['corso'],
                            'adId': info_json['adId'],
                            'telefono': info_json['telefono'],
                            'email': info_json['email'],
                            'link': info_json['link'],
                            'ugov_id': info_json['ugov_id'],
                            'url_pic': img.decode('utf-8')
                        })
                        array.append(item)
                else:
                    return {'errMsg': _response['retErrMsg']}, response.status_code

                return array, 200

            except requests.exceptions.HTTPError as e:
                return {'errMsg': str(e)}, 500
            except requests.exceptions.ConnectionError as e:
                return {'errMsg': str(e)}, 500
            except requests.exceptions.Timeout as e:
                return {'errMsg': str(e)}, 500
            except requests.exceptions.RequestException as e:
                return {'errMsg': str(e)}, 500
            except:
                return {'errMsg': 'generic error'}, 500
        else:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


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
