import io
import os
import random
import ssl
import string
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from app.config import Config
from bs4 import BeautifulSoup

import feedparser


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

import requests
from bs4 import BeautifulSoup
from flask import g, send_file, request
from flask_restplus import Resource

from app import api
from app.apis.uniparthenope.v1.login_v1 import token_required, token_required_general


url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def randomword(length):
    letters = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))


def extractData(data):
    data_split = data.split()[0]
    export_data = datetime.strptime(data_split, '%d/%m/%Y')

    return export_data


# ------------- ANAGRAFICA -------------


parser = api.parser()
parser.add_argument('Id', type=int, required=True, help='User personId/docenteId')


class Anagrafica(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, Id):
        """Get personal info"""

        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + g.token
        }

        try:
            res = requests.request("GET", url + "anagrafica-service-v2/persone/" + Id, headers=headers, timeout=5)
            _response = res.json()

            if res.status_code == 200:
                return {
                    'nome': _response['nome'],
                    'cognome': _response['cognome'],
                    'codFis': _response['codFis'],
                    'dataNascita': _response['dataNascita'],
                    'desCittadinanza': _response['desCittadinanza'],
                    'email': _response['email'],
                    'emailAte': _response['emailAte'],
                    'sesso': _response['sesso'],
                    'telRes': _response['telRes']
                }, 200
            elif res.status_code == 403:
                res = requests.request("GET", url + "anagrafica-service-v2/docenti/" + Id, headers=headers, timeout=5)
                _response = res.json()

                print(_response)

                if res.status_code == 200:
                    return {
                        'nome': _response[0]['docenteNome'],
                        'cognome': _response[0]['docenteCognome'],
                        'codFis': _response[0]['codFis'],
                        'dataNascita': _response[0]['dataNascita'],
                        'emailAte': _response[0]['eMail'],
                        'sesso': _response[0]['sesso'],
                        'telRes': _response[0]['cellulare'],
                        'ruolo': _response[0]['ruoloDocDes'],
                        'settore': _response[0]['settDes']
                    }, 200
                else:
                    return {'errMsg': _response["retErrMsg"]}, res.status_code
            else:
                return {'errMsg': _response["retErrMsg"]}, res.status_code
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
            res = requests.get(url + "anagrafica-service-v2/persone/" + personId + "/foto", headers=headers, timeout=5,
                               stream=True)
            if res.status_code == 200:
                return send_file(
                    io.BytesIO(res.content),
                    attachment_filename='image.jpg',
                    mimetype='image/jpg',
                    cache_timeout=-1
                )
            else:
                return send_file(
                    io.FileIO('./images/default_pic.jpg'),
                    attachment_filename='image.jpg',
                    mimetype='image/jpg',
                    cache_timeout=-1
                )

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
                # random_seq = randomword(8)
                # res = requests.get("https://www.uniparthenope.it/sites/default/files/styles/fototessera__175x200_/public/ugov_wsfiles/foto/ugov_fotopersona_0000000000" + idAb + ".jpg?itok=" + random_seq, stream=True)
                img_url = "https://www.uniparthenope.it/sites/default/files/styles/fototessera__175x200_/public/ugov_wsfiles/foto/ugov_fotopersona_0000000000" + str(
                    idAb) + ".jpg"
                res = requests.request("GET", img_url, verify=False, timeout=5)

                if res.status_code == 200:
                    return send_file(
                        io.BytesIO(res.content),
                        attachment_filename='image.jpg',
                        mimetype='image/jpg',
                        cache_timeout=-1
                    )
                else:
                    return send_file(
                        io.FileIO('./images/default_pic.jpg'),
                        attachment_filename='image.jpg',
                        mimetype='image/jpg',
                        cache_timeout=-1
                    )

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
            return {'errMsg': 'Wring username/pass'}, g.status


# ------------- ANNO ACCADEMICO CORRENTE -------------


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
                                        headers=headers, timeout=5)
            _response = response.json()

            if response.status_code == 200:
                date = datetime.today()
                curr_day = datetime(date.year, date.month, date.day)

                max_year = _response[0]['aaSesId']

                for i in range(0, len(_response)):
                    if _response[i]['aaSesId'] == max_year:
                        startDate = extractData(_response[i]['dataInizio'])
                        endDate = extractData(_response[i]['dataFine'])

                        if startDate <= curr_day <= endDate:
                            curr_sem = _response[i]['des']

                            response_aa = requests.request("GET",
                                                        url + "servizi-service-v1/annoRif/DR_SUA", headers=headers, timeout=5)
                            _response_aa = response_aa.json()

                            if response_aa.status_code == 200:

                                if curr_sem == "Sessione Estiva" or curr_sem == "Sessione Anticipata" or curr_sem == "Sessione Straordinaria":

                                    return {
                                               'curr_sem': _response[i]['des'],
                                               'semestre': "Secondo Semestre",
                                               'aa_accad': str(_response_aa['aaId'])
                                           }, 200
                                else:
                                    return {
                                               'curr_sem': _response[i]['des'],
                                               'semestre': "Primo Semestre",
                                               'aa_accad': str(_response_aa['aaId'])
                                           }, 200
                            else:
                                return {'errMsg': _response_aa['retErrMsg']}, response_aa.status_code

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


# ------------- AD RECENTE -------------
# TODO DA ELIMINARE???

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
            response = requests.request("GET", url + "logistica-service-v1/logistica?adId=" + adId, headers=headers, timeout=5)
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


# ------------- INFO CORSI -------------


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
                                        headers=headers, timeout=5)
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
            return {'errMsg': 'generic error'}, 500


# ------------- INFO PERSONE -------------
# TODO DA ELIMINARE???

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


# ------------- NEWS RSS -------------


parser = api.parser()
parser.add_argument('size', type=int, required=True, help='Numero di notizie')


class RSSNews(Resource):
    def get(self, size):
        """Get news"""

        try:
            feed = feedparser.parse("https://www.uniparthenope.it/rss/tutte-le-news")

            notizie = []

            if size > len(feed['entries']):
                size = len(feed['entries'])

            for i in range(0, size):
                notizia = {}

                parsed_html = BeautifulSoup(feed['entries'][i]['summary'], features="html.parser")
                if 'image' in parsed_html.find('div', attrs={'class': 'field-name-field-video'}).find('a').attrs['type']:
                    image = parsed_html.find('div', attrs={'class': 'field-name-field-video'}).find('a').attrs['href']
                else:
                    image = "~/images/image1.jpg"

                html = ""
                for p in parsed_html.find('div', attrs={'class': 'field-name-field-descrizione'}).find_all('p'):
                    html += str(p)

                notizia.update({
                    'titolo': feed['entries'][i]['title'],
                    'link': feed['entries'][i]['link'],
                    'data': feed['entries'][i]['published'],
                    'HTML': html,
                    'image': image
                })
                notizie.append(notizia)
            return notizie, 200
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


# ------------- AVVISI RSS -------------


parser = api.parser()
parser.add_argument('size', type=int, required=True, help='Numero di avvisi')


class RSSAvvisi(Resource):
    def get(self, size):
        """Get avvisi"""

        try:
            feed = feedparser.parse("https://www.uniparthenope.it/rss/tutti-gli-avvisi")

            avvisi = []

            if size > len(feed['entries']):
                size = len(feed['entries'])

            for i in range(0, size):
                avviso = {}
                html = ""
                abstract = ""

                parsed_html = BeautifulSoup(feed['entries'][i]['summary'], features="html.parser")
                for p in parsed_html.find('div', attrs={'class': 'field-name-field-descrizione'}).find_all('p'):
                    html += str(p)
                if parsed_html.find('div', attrs={'class': 'field-name-body'}) is not None:
                    for p in parsed_html.find('div', attrs={'class': 'field-name-body'}).find_all('p'):
                        abstract += str(p)
                avviso.update({
                    'titolo': feed['entries'][i]['title'],
                    'link': feed['entries'][i]['link'],
                    'data': feed['entries'][i]['published'],
                    'abstract': abstract,
                    'HTML': html
                })
                avvisi.append(avviso)
            return avvisi, 200

        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


# ------------- PRIVACY -------------


class Privacy(Resource):
    def get(self):
        """Get privacy policy"""

        text = '<p>Come &egrave; noto il Regolamento Europeo 2016/679 GDPR (General Data Protection Regulation), relativo alla protezione delle persone fisiche con riguardo al trattamento dei dati personali applicabile dal 25 maggio 2018, prescrive, all&rsquo;art.37, l&rsquo;obbligo, per le amministrazioni pubbliche, di nominare il Responsabile della protezione dei dati (DPO). <br>Si comunica che per l&rsquo;Universit&agrave; Parthenope &egrave; stato nominato quale Responsabile della protezione dei dati la Prof. Anna Papa, delegato per gli Affari Giuridici e Istituzionali (D.R. 311 del 14 maggio 2018). <br>Nell&rsquo;ambito delle funzioni attribuite con tale mandato, come previsto dall&rsquo;art. 39 del Regolamento Europeo Privacy, la Prof.. Papa &nbsp;in particolare: </p> <p>&nbsp;- collabora con il titolare al fine dell&rsquo;assunzione di ogni azione necessaria a dare attuazione alla nuova normativa; <br>- svolge attivit&agrave; di informazione e consulenza nei confronti dei responsabili del trattamento riguardo agli obblighi derivanti dal regolamento europeo e da altre disposizioni in materia di protezione dei dati;<br>&nbsp;- controlla l&rsquo;osservanza del regolamento nell&rsquo;ambito di applicazione.</p><p>A supporto dell&rsquo;attivit&agrave; del DPO, con O.d.s del Direttore Generale n.18 del 14/05/2018 &egrave; stato costituito il gruppo di lavoro &ldquo;protezione dei dati personali&rdquo;, i cui contatti sono di seguito riportati nella presente pagina.</p><p>Nell&rsquo;ambito degli adempimenti previsti dal Regolamento Europeo (GDPR) l&rsquo;Universit&agrave; Parthenope ha provveduto ad istituire il &ldquo;Registro delle attivit&agrave; di trattamento dei dati&rdquo; del Titolare previsto dall&rsquo;art. 30 del citato regolamento (nota prot.&nbsp;<a href=\"tel:0031524/2018\">0031524/2018</a>).</p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/privacy/procedura_data_breach.pdf\" target=\"_blank\" title=\"PROCEDURA DATA BREACH  - The document opens in new window\" type=\"application/pdf; length=574922\">PROCEDURA DATA BREACH</a></span></p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/informativa_parthenope_concorsi_e_selezioni_ga_18.10.2018.pdf\" target=\"_blank\" title=\"Informativa Concorsi e selezioni  - The document opens in new window\" type=\"application/pdf; length=283728\">Informativa Concorsi e selezioni</a></span></p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/documenti/informativa_studenti.pdf\" target=\"_blank\" title=\"Informativa Studente  - The document opens in new window\">Informativa Studente</a></span></p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/informativa_orientamento_19.10.2018.pdf\" target=\"_blank\" title=\"Informativa Orientamento  - The document opens in new window\" type=\"application/pdf; length=285722\">Informativa Orientamento</a></span></p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/informativa_terzi_e_placement.pdf\" target=\"_blank\" title=\"Informativa Terzi e Placement  - The document opens in new window\" type=\"application/pdf; length=248033\">Informativa Terzi e Placement</a></span></p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/privacy/informativa_sito_web.pdf\" target=\"_blank\" title=\"Informativa Sito Web  - The document opens in new window\" type=\"application/pdf; length=527764\">Informativa Sito Web</a></span><span><a href=\"https://www.uniparthenope.it/sites/default/files/informativa_parthenope_idem.pdf\" style=\"box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;\" target=\"_blank\" title=\"  - The document opens in new window\"></a></span></p><p><span><a href=\"https://www.uniparthenope.it/sites/default/files/privacy/informativa_sito_web.pdf\" rel=\"noopener noreferrer\" target=\"_blank\" title=\"informativa_sito_web.pdf  - The document opens in new window\" type=\"application/pdf; length=527764\">Informativa_sito_web.pdf</a></span></p>'

        return {'privacy': text}, 200


# ------------- PLACES -------------


class Sedi(Resource):
    def get(self):
        """Get university places"""

        return Config.SEDI_UNP, 200
