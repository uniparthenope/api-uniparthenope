import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from io import BytesIO
import qrcode
import io

import requests
from bs4 import BeautifulSoup
from flask import g, send_file, Response
from flask_restplus import Resource

from app import api
from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def extractData(data):
    data_split = data.split()[0]
    export_data = datetime.strptime(data_split, '%d/%m/%Y')

    return export_data


# ------------- PERSONAL IMAGE -------------


parser = api.parser()
parser.add_argument('personId', type=int, required=True, help='User personId')


class PersonalImage(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    @ns.produces(['image/jpg'])
    def get(self, personId):
        """Get personale image"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            res = requests.get(url + "anagrafica-service-v2/persone/" + personId + "/foto", headers=headers, stream=True)
            if res.status_code == 200:
                return send_file(
                    io.BytesIO(res.content),
                    attachment_filename='image.jpg',
                    mimetype='image/jpg'
                )
            else:
                _response = res.json()
                return {'errMsg': _response["retErrMsg"]}, res.status_code

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


# ------------- QR-CODE -------------


parser = api.parser()
parser.add_argument('userId', type=str, required=True, help='User userId')


class QrCode(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.produces(['image/jpg'])
    def get(self, userId):
        """Get qr-code image"""

        pil_img = qrcode.make(userId)
        img_io = BytesIO()
        pil_img.save(img_io, 'JPG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpg')


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
            response = requests.request("GET", url + "calesa-service-v1/sessioni?cdsId=" + cdsId + "&order=-aaSesId", headers=headers)
            _response = response.json()

            date = datetime.today()
            curr_day = datetime(date.year, date.month, date.day)

            max_year = _response[0]['aaSesId']

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


# ------------- INFO PERSONE -------------


parser = api.parser()
parser.add_argument('nome_completo', type=str, required=True, help='Nome e Cognome professore')


class InfoPersone(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self,nome_completo):
        """Get info person"""

        nome = nome_completo.replace(" ", "+")
        url = 'https://www.uniparthenope.it/rubrica?nome_esteso_1=' + nome

        try:
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
                    tel_finale = "N/A"

                email = ul.find('div', attrs={'class': 'views-field views-field-contatto-email'})
                email_finale = email.find('span', attrs={'class': 'field-content'})

                scheda = ul.find('div', attrs={'class': 'views-field views-field-view-uelement'})
                scheda_finale = scheda.find('span', attrs={'class': 'field-content'})

                for a in scheda_finale.find_all('a', href=True):
                    link = a['href']

                link_pers = str(link).split("/")[-1]

                response = urllib.request.urlopen(link)
                webContent = response.read()

                parsed = BeautifulSoup(webContent,'html.parser')
                div = parsed.find('div', attrs={'class': 'views-field views-field-field-ugov-foto'})
                img = div.find('img', attrs={'class': 'img-responsive'})


                prof = ({
                    'telefono' : str(tel_finale),
                    'email' : str(email_finale.text.rstrip()),
                    'link' : str(link),
                    'ugov_id' : link_pers,
                    'url_pic' : str(img['src'])
                })
            else:
                prof = ({
                    'telefono': "",
                    'email': "",
                    'link': "",
                    'ugov_id': "",
                    'url_pic': "https://www.uniparthenope.it/sites/default/files/styles/fototessera__175x200_/public/default_images/ugov_fotopersona.jpg"
                })

            return prof, 200

        except:
            return {'errMsg': 'generic error'}, 500