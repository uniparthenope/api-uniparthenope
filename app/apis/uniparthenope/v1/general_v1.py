from app.apis.uniparthenope.v1.login_v1 import token_required
from flask import g
from app import api
from flask_restplus import Resource
import requests
from datetime import datetime, timedelta

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def extractData(data):
    data_split = data.split()[0]
    export_data = datetime.strptime(data_split, '%d/%m/%Y')

    return export_data


# ------------- ANNO ACCADEMICO -------------


parser = api.parser()
parser.add_argument('cdsId', type=str, required=True, help='User cdsId')


class CurrentAA(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, cdsId):
        """Get current AA"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "calesa-service-v1/sessioni?cdsId=" + cdsId, headers=headers)
            _response = response.json()

            date = datetime.today()
            curr_day = datetime(date.year, date.month, date.day)

            max_year = 0
            for i in range(0, len(_response)):
                if _response[i]['aaSesId'] > max_year:
                    max_year = _response[i]['aaSesId']

            for i in range(0, len(_response)):
                if _response[i]['aaSesId'] == max_year:
                    startDate = extractData(_response[i]['dataInizio'])
                    endDate = extractData(_response[i]['dataFine'])

                    if (curr_day >= startDate and curr_day <= endDate):
                        print("Inizio: " + str(startDate))
                        print("Fine: " + str(endDate))
                        print("Oggi: " + str(curr_day))

                        curr_sem = _response[i]['des']
                        academic_year = str(_response[i]['aaSesId']) + " - " + str(_response[i]['aaSesId'] + 1)

                        if curr_sem == "Sessione Estiva" or curr_sem == "Sessione Anticipata" or curr_sem == "Sessione Straordinaria" :
                            return {
                                'curr_sem': _response[i]['des'],
                                'semestre': "Secondo Semestre",
                                'aa_accad': academic_year
                            }, 200
                        else:
                            return {
                                'curr_sem': _response[i]['des'],
                                'semestre': "Primo Semestre",
                                'aa_accad': academic_year
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


# ------------- ANNO ACCADEMICO -------------


parser = api.parser()
parser.add_argument('adId', type=str, required=True, help='User adId')


class RecentAD(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, adId):
        """Get recent AD"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }
        try:
            response = requests.request("GET", url + "logistica-service-v1/logistica?adId=" + adId, headers=headers)
            _response = response.json()

            max_year = 0
            if response.status_code == 200:
                for i in range(0, len(_response)):
                    if _response[i]['chiaveADFisica']['aaOffId'] > max_year:
                        max_year = _response[i]['chiaveADFisica']['aaOffId']

                for i in range(0, len(_response)):
                    if _response[i]['chiaveADFisica']['aaOffId'] == max_year:
                        return {'adLogId': _response[i]['chiavePartizione']['adLogId'],
                                        'inizio': _response[i]['dataInizio'].split()[0],
                                        'fine': _response[i]['dataFine'].split()[0],
                                        'ultMod': _response[i]['dataModLog'].split()[0]
                                        },200
            else:
                return {'stsErr': "N"}, 500

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


# ------------- ANNO ACCADEMICO -------------


parser = api.parser()
parser.add_argument('adLogId', type=str, required=True, help='Exam adLogId')


class InfoCourse(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, adLogId):
        """Get info course"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            response = requests.request("GET", url + "logistica-service-v1/logistica/" + adLogId + "/adLogConSyllabus", headers=headers)
            _response = response.json()

            if response.status_code == 200:
                return {'contenuti': _response[0]['SyllabusAD'][0]['contenuti'],
                            'metodi': _response[0]['SyllabusAD'][0]['metodiDidattici'],
                            'verifica': _response[0]['SyllabusAD'][0]['modalitaVerificaApprendimento'],
                            'obiettivi': _response[0]['SyllabusAD'][0]['obiettiviFormativi'],
                            'prerequisiti': _response[0]['SyllabusAD'][0]['prerequisiti'],
                            'testi': _response[0]['SyllabusAD'][0]['testiRiferimento'],
                            'altro': _response[0]['SyllabusAD'][0]['altreInfo']
                },200

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