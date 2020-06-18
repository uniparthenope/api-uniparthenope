from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general
from flask import g
from app import api
from flask_restplus import Resource
import requests

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
            response = requests.request("GET", url + "anagrafica-service-v2/carriere/" + stuId, headers=headers)
            _response = response.json()

            #TODO Add search in GA table 'cdsId' and return GA id

            return {'aaId': _response['aaId'],
                    'dataIscr': _response['dataIscr'],
                    'facCod': _response['facCod'],
                    'facCsaCod': _response['facCsaCod'],
                    'facDes': _response['facDes'],
                    'sedeId': _response['sedeId'],
                    'sediDes': _response['sediDes']
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
            response = requests.request("GET", url + "piani-service-v1/piani/" + stuId, headers=headers)
            _response = response.json()
            pianoId = _response[0]['pianoId']

            return {'pianoId': pianoId}, 200

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
                                        headers=headers)
            _response = response.json()

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
            response = requests.request("GET", url + "libretto-service-v1/libretti/" + matId + "/stats",
                                        headers=headers)
            _response = response.json()

            if len(_response) != 0:
                totAdSuperate = _response['numAdSuperate'] + _response['numAdFrequentate']
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
            response = requests.request("GET", url + "piani-service-v1/piani/" + stuId + "/" + pianoId, headers=headers)
            _response = response.json()

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
                                        headers=headers)

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
            return {'errMsg': e}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': e}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': e}, 500
        except requests.exceptions.RequestException as e:
            return {'errMsg': e}, 500
        except:
            return {'errMsg': 'generic error'}, 500


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

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "calesa-service-v1/appelli/" + cdsId + "/" + adId, headers=headers)
            _response = response.json()

            for i in range(0, len(_response)):
                if _response[i]['stato'] == "I" or _response[i]['stato'] == "P":
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
            response = requests.request("GET", url + "calesa-service-v1/appelli/" + cdsId + "/" + adId + "/" + appId + "/iscritti/" + stuId, headers=headers)
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
            return {'errMsg': e}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': e}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': e}, 500
        except requests.exceptions.RequestException as e:
            return {'errMsg': e}, 500
        except:
            return {'errMsg': 'generic error'}, 500


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
            response = requests.request("GET", url + "calesa-service-v1/prenotazioni/" + matId, headers=headers)
            _response = response.json()

            # print(_response)
            for i in range(0, len(_response)):
                response2 = requests.request("GET", url + "calesa-service-v1/appelli/" + str(_response[i]['cdsId']) + "/" + str(_response[i]['adId']) + "/" + str(_response[i]['appId']), headers=headers)
                _response2 = response2.json()

                for x in range(0, len(_response2['turni'])):
                    if _response2['turni'][x]['appLogId'] == _response[i]['appLogId']:
                        if _response2['stato'] is not "C":
                            item = ({
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


# ------------- EXAMS TO FREQ -------------


parser = api.parser()
parser.add_argument('stuId', type=str, required=True, help='User stuId')
parser.add_argument('pianoId', type=str, required=True, help='User pianoId')
parser.add_argument('matId', type=str, required=True, help='User matId')


@ns.doc(parser=parser)
class ExamsToFreq(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, stuId, pianoId, matId):
        """Get exams to frequent"""

        my_exams = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "piani-service-v1/piani/" + stuId + "/" + pianoId, headers=headers)
            _response = response.json()

            # print("JSON (examsToFreq --> 1): " + str(_response))
            # print("JSON (Lunghezza --> 1)" + str(len(_response['attivita'])))

            for i in range(0, len(_response['attivita'])):
                if _response['attivita'][i]['sceltaFlg'] == 1:
                    adId = str(_response['attivita'][i]['chiaveADContestualizzata']['adId'])
                    adSceId = _response['attivita'][i]['adsceAttId']

                    # print("Ads ID: " + str(adSceId))
                    response_2 = requests.request("GET", url + "libretto-service-v1/libretti/" + matId + "/righe/" + str(adSceId), headers=headers)
                    # print("JSON (examsToFreq --> 2): " + str(response_2.json()))

                    if response_2.status_code == 500 or response_2.status_code == 404:
                        print('ERRORE --> 2')
                    else:
                        _response2 = response_2.json()

                        if _response2['statoDes'] != "Superata" and len(_response2) != 0:
                            # print("ADID --> 2=" + adId)
                            # print("ADSCEID --> 2 = " + str(adSceId))

                            response_3 = requests.request("GET", url + "libretto-service-v1/libretti/" + matId + "/righe/" + str(adSceId) + "/partizioni", headers=headers)
                            # print("JSON (examsToFreq --> 3): " + str(response_3.json()))

                            if response_3.status_code == 500 or response_3.status_code == 404:
                                print('Response 3 non idoneo!skip')
                            else:
                                _response3 = response_3.json()

                                if len(_response3) == 0:
                                    # print("Response3 non idoneo")
                                    response_4 = requests.request("GET", url + "logistica-service-v1/logistica?adId=" + adId, headers=headers)
                                    _response4 = response_4.json()
                                    # print("JSON (examsToFreq --> 4 (IF)): " + str(response_4.json()))

                                    max_year = 0
                                    if response_4.status_code == 200:
                                        for x in range(0, len(_response4)):
                                            if _response4[x]['chiaveADFisica']['aaOffId'] > max_year:
                                                max_year = _response4[x]['chiaveADFisica']['aaOffId']

                                        for x in range(0, len(_response4)):
                                            if _response4[x]['chiaveADFisica']['aaOffId'] == max_year:
                                                actual_exam = ({
                                                    'nome': _response['attivita'][i]['adLibDes'],
                                                    'codice': _response['attivita'][i]['adLibCod'],
                                                    'adId': _response['attivita'][i]['chiaveADContestualizzata']['adId'],
                                                    'CFU': _response['attivita'][i]['peso'],
                                                    'annoId': _response['attivita'][i]['scePianoId'],
                                                    'docente': "N/A",
                                                    'docenteID': "N/A",
                                                    'semestre': "N/A",
                                                    'adLogId': _response4[x]['chiavePartizione']['adLogId'],
                                                    'inizio': _response4[x]['dataInizio'].split()[0],
                                                    'fine': _response4[x]['dataFine'].split()[0],
                                                    'ultMod': _response4[x]['dataModLog'].split()[0]
                                                })
                                                my_exams.append(actual_exam)

                                else:

                                    response_4 = requests.request("GET", url + "logistica-service-v1/logistica?adId=" + adId, headers=headers)
                                    _response4 = response_4.json()
                                    # print("JSON (examsToFreq --> 4) (ELSE): " + str(response_4.json()))

                                    max_year = 0
                                    if response_4.status_code == 200:
                                        for x in range(0, len(_response4)):
                                            if _response4[x]['chiaveADFisica']['aaOffId'] > max_year:
                                                max_year = _response4[x]['chiaveADFisica']['aaOffId']

                                        for x in range(0, len(_response4)):
                                            if _response4[x]['chiaveADFisica']['aaOffId'] == max_year:
                                                actual_exam = ({
                                                    'nome': _response['attivita'][i]['adLibDes'],
                                                    'codice': _response['attivita'][i]['adLibCod'],
                                                    'adId': _response['attivita'][i]['chiaveADContestualizzata'][
                                                        'adId'],
                                                    'CFU': _response['attivita'][i]['peso'],
                                                    'annoId': _response['attivita'][i]['scePianoId'],
                                                    'docente': _response3[0]['cognomeDocTit'].capitalize() + " " +
                                                               _response3[0]['nomeDoctit'].capitalize(),
                                                    'docenteID': _response3[0]['docenteId'],
                                                    'semestre': _response3[0]['partEffCod'],
                                                    'adLogId': _response4[x]['chiavePartizione']['adLogId'],
                                                    'inizio': _response4[x]['dataInizio'].split()[0],
                                                    'fine': _response4[x]['dataFine'].split()[0],
                                                    'ultMod': _response4[x]['dataModLog'].split()[0]
                                                })
                                                my_exams.append(actual_exam)
            return my_exams, 200
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


# ------------- GET PROFESSORS -------------


parser = api.parser()
parser.add_argument('aaId', type=str, required=True, help='User stuId')
parser.add_argument('cdsId', type=str, required=True, help='User pianoId')


@ns.doc(parser=parser)
class getProfessors(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, aaId, cdsId):
        """Get professor's list"""

        headers = {
            'Content-Type': "application/json",
        }

        array = []

        if g.status == 200:
            try:
                response = requests.request("GET", url + "offerta-service-v1/offerte/" + aaId + "/" + cdsId + "/docentiPerUD", headers=headers)
                _response = response.json()

                if response.status_code == 200:
                    for i in range(0, len(_response)):
                        item = ({
                            'docenteNome': _response[i]['docenteNome'],
                            'docenteCognome': _response[i]['docenteCognome'],
                            'docenteId':_response[i]['docenteId'],
                            'docenteMat': _response[i]['docenteMatricola'],
                            'corso': _response[i]['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adDes'],
                            'adId': _response[i]['chiaveUdContestualizzata']['chiaveAdContestualizzata']['adId']
                        })
                        array.append(item)

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

# ------------- TAXES -------------


parser = api.parser()
parser.add_argument('persId', type=str, required=True, help='User persId')
parser.add_argument('pagatoFlg', type=str, required=True, help='Taxes to pay')


@ns.doc(parser=parser)
class Taxes(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, persId, pagatoFlg):
        """Taxes situation"""

        array = []

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "tasse-service-v1/lista-fatture?persId=" + persId + "&pagatoFlg=" + pagatoFlg, headers=headers)
            _response = response.json()

            if response.status_code == 200:
                for i in range(0, len(_response)):
                    if pagatoFlg == '0':
                        item = ({
                            'desc': _response[i]['desMav1'],
                            'fattId': _response[i]['fattId'],
                            'importo': _response[i]['importoFattura'],
                            'iuv': _response[i]['iuv'],
                            'scadFattura': _response[i]['scadFattura']
                        })
                        array.append(item)
                    else:
                        item = ({
                            'desc': _response[i]['desMav1'],
                            'fattId': _response[i]['fattId'],
                            'importo': _response[i]['importoFattura'],
                            'dataPagamento': _response[i]['dataPagamento'],
                            'scadFattura': _response[i]['scadFattura'],
                            'iur': _response[i]['iur'],
                            'nBollettino': _response[i]['nBollettino']
                        })
                        array.append(item)

                return array, 200
            else:
                return {'errMsg': _response['retErrMsg']}, _response['statusCode']

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