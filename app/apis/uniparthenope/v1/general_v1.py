import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
import io
import feedparser
import html2text
import random, string


import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

import requests
from bs4 import BeautifulSoup
from flask import g, send_file, Response, request
from flask_restplus import Resource

from app import api
from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

def randomword(length):
   letters = string.ascii_lowercase+string.digits+string.ascii_uppercase
   return ''.join(random.choice(letters) for i in range(length))

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
            res = requests.get(url + "anagrafica-service-v2/persone/" + personId + "/foto", headers=headers,
                               stream=True)
            if res.status_code == 200:
                return send_file(
                    io.BytesIO(res.content),
                    attachment_filename='image.jpg',
                    mimetype='image/jpg',
                    cache_timeout=-1
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


# ------------- PROFESSOR IMAGE -------------


parser = api.parser()
parser.add_argument('idAb', type=int, required=True, help='Professor idAb')


class ProfImage(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.produces(['image/jpg'])
    def get(self, idAb):
        """Get personale image"""

        if g.status == 200:
            try:
                random_seq = randomword(8)
                res = requests.get("https://www.uniparthenope.it/sites/default/files/styles/fototessera__175x200_/public/ugov_wsfiles/foto/ugov_fotopersona_0000000000" + idAb + ".jpg?itok=" + random_seq, stream=True)
                print("HERE")
                print(res)
                if res.status_code == 200:
                    print("Ok")
                    return send_file(
                        io.BytesIO(res.content),
                        attachment_filename='image.jpg',
                        mimetype='image/jpg',
                        cache_timeout=-1
                    )
                else:
                    print("Wrong")
                    #_response = res.json()
                    #return {'errMsg': "Picture Error"}

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
            return {'errMsg': 'Wring username/pass'}, g.status


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
            response = requests.request("GET", url + "calesa-service-v1/sessioni?cdsId=" + cdsId + "&order=-aaSesId",
                                        headers=headers)
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

                        if curr_sem == "Sessione Estiva" or curr_sem == "Sessione Anticipata" or curr_sem == "Sessione Straordinaria":
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
                                }, 200
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
            response = requests.request("GET", url + "logistica-service-v1/logistica/" + adLogId + "/adLogConSyllabus",
                                        headers=headers)
            _response = response.json()

            if response.status_code == 200:
                return {'contenuti': _response[0]['SyllabusAD'][0]['contenuti'],
                        'metodi': _response[0]['SyllabusAD'][0]['metodiDidattici'],
                        'verifica': _response[0]['SyllabusAD'][0]['modalitaVerificaApprendimento'],
                        'obiettivi': _response[0]['SyllabusAD'][0]['obiettiviFormativi'],
                        'prerequisiti': _response[0]['SyllabusAD'][0]['prerequisiti'],
                        'testi': _response[0]['SyllabusAD'][0]['testiRiferimento'],
                        'altro': _response[0]['SyllabusAD'][0]['altreInfo']
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


# ------------- INFO PERSONE -------------


parser = api.parser()
parser.add_argument('nome_completo', type=str, required=True, help='Nome e Cognome professore')


class InfoPersone(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, nome_completo):
        """Get info person"""

        nome = nome_completo.replace(" ", "+")
        url = 'https://www.uniparthenope.it/rubrica?nome_esteso_1=' + nome

        if g.status == 200:
            #try:
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

                parsed = BeautifulSoup(webContent, 'html.parser')
                div = parsed.find('div', attrs={'class': 'views-field views-field-field-ugov-foto'})
                img = div.find('img', attrs={'class': 'img-responsive'})

                prof = ({
                    'telefono': str(tel_finale),
                    'email': str(email_finale.text.rstrip()),
                    'link': str(link),
                    'ugov_id': link_pers,
                    'url_pic': str(img['src'])
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

            #except:
            #    return {'errMsg': 'generic error'}, 500
        else:
            return {'errMsg': 'generic error'}, g.status


# ------------- NEWS RSS -------------


class RSSNews(Resource):
    def get(self):
        """Get news"""

        try:
            feed = feedparser.parse("https://www.uniparthenope.it/rss.xml")
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True

            start = '<a href="'
            end = '" type='

            news = []

            for i in range(0, len(feed['entries'])):
                img = ""
                text_string = (BeautifulSoup(feed['entries'][i]['summary'], features="html.parser")).get_text()
                text_string = text_string.split("Foto/Video:")[0]

                if "Foto/Video" in feed['entries'][i]['summary']:
                    text = feed['entries'][i]['summary']

                    while start in text and end in text:
                        s_index = text.find(start)
                        e_index = text.find(end) + len(end)

                        img = text[s_index:e_index]
                        title = h.handle(img).strip()
                        text = text.replace(img, title)

                    img = img.replace(start, "")
                    img = img.replace(end, "")

                if "Testo:" in text_string:
                    text_string = text_string.split("Testo:")[1]

                article = {}
                article.update({
                    'titolo': feed['entries'][i]['title'],
                    'link': feed['entries'][i]['link'],
                    'data': feed['entries'][i]['published'],
                    'image': img,
                    'HTML': feed['entries'][i]['summary'],
                    'TEXT': text_string
                })
                news.append(article)

            return news, 200

        except:
            return {'errMsg': 'generic error'}, 500