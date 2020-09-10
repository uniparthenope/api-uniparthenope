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
from shutil import copyfileobj
from tempfile import NamedTemporaryFile

import feedparser
import html2text


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
            res = requests.request("GET", url + "anagrafica-service-v2/persone/" + Id, headers=headers)
            _response = res.json()

            if res.status_code == 200:
                return {
                    'dataNascita': _response['dataNascita'],
                    'desCittadinanza': _response['desCittadinanza'],
                    'email': _response['email'],
                    'emailAte': _response['emailAte'],
                    'sesso': _response['sesso'],
                    'telRes': _response['telRes']
                }, 200
            elif res.status_code == 403:
                res = requests.request("GET", url + "anagrafica-service-v2/docenti/" + Id, headers=headers)
                _response = res.json()

                if res.status_code == 200:
                    return {
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
                return send_file(
                    io.FileIO('./images/default_pic.jpg'),
                    attachment_filename='image.jpg',
                    mimetype='image/jpg',
                    cache_timeout=-1
                )

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
                res = requests.request("GET", img_url, verify=False)

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
                                        headers=headers)
            _response = response.json()

            if response.status_code == 200:
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


# ------------- AD RECENTE -------------


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
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


# ------------- AVVISI RSS -------------


class RSSAvvisi(Resource):
    def get(self):
        """Get news"""

        try:
            feed = feedparser.parse("https://www.uniparthenope.it/rss.xml")

            avvisi = []

            for i in range(0, len(feed['entries'])):
                avviso = {}
                avviso.update({
                    'titolo': feed['entries'][i]['title'],
                    'link': feed['entries'][i]['link'],
                    'data': feed['entries'][i]['published'],
                    'HTML': feed['entries'][i]['summary'],
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

        text = '<p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;">Come &egrave; noto il Regolamento Europeo 2016/679 GDPR (General Data Protection Regulation), relativo alla protezione delle persone fisiche con riguardo al trattamento dei dati personali applicabile dal 25 maggio 2018, prescrive, all&rsquo;art.37, l&rsquo;obbligo, per le amministrazioni pubbliche, di nominare il Responsabile della protezione dei dati (DPO).<br style="box-sizing: border-box;">Si comunica che per l&rsquo;Universit&agrave; Parthenope &egrave; stato nominato quale Responsabile della protezione dei dati la Prof. Anna Papa, delegato per gli Affari Giuridici e Istituzionali (D.R. 311 del 14 maggio 2018).<br style="box-sizing: border-box;">Nell&rsquo;ambito delle funzioni attribuite con tale mandato, come previsto dall&rsquo;art. 39 del Regolamento Europeo Privacy, la Prof.. Papa &nbsp;in particolare:</p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;">&nbsp;- collabora con il titolare al fine dell&rsquo;assunzione di ogni azione necessaria a dare attuazione alla nuova normativa;<br style="box-sizing: border-box;">- svolge attivit&agrave; di informazione e consulenza nei confronti dei responsabili del trattamento riguardo agli obblighi derivanti dal regolamento europeo e da altre disposizioni in materia di protezione dei dati;<br style="box-sizing: border-box;">&nbsp;- controlla l&rsquo;osservanza del regolamento nell&rsquo;ambito di applicazione.</p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;">A supporto dell&rsquo;attivit&agrave; del DPO, con O.d.s del Direttore Generale n.18 del 14/05/2018 &egrave; stato costituito il gruppo di lavoro &ldquo;protezione dei dati personali&rdquo;, i cui contatti sono di seguito riportati nella presente pagina.</p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;">Nell&rsquo;ambito degli adempimenti previsti dal Regolamento Europeo (GDPR) l&rsquo;Universit&agrave; Parthenope ha provveduto ad istituire il &ldquo;Registro delle attivit&agrave; di trattamento dei dati&rdquo; del Titolare previsto dall&rsquo;art. 30 del citato regolamento (nota prot.&nbsp;<a href="tel:0031524/2018" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline;">0031524/2018</a>).</p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a class="application-pdf" href="https://www.uniparthenope.it/sites/default/files/privacy/procedura_data_breach.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="PROCEDURA DATA BREACH  - The document opens in new window" type="application/pdf; length=574922">PROCEDURA DATA BREACH</a></span></p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a class="application-pdf" href="https://www.uniparthenope.it/sites/default/files/informativa_parthenope_concorsi_e_selezioni_ga_18.10.2018.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="Informativa Concorsi e selezioni  - The document opens in new window" type="application/pdf; length=283728">Informativa Concorsi e selezioni</a></span></p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a href="https://www.uniparthenope.it/sites/default/files/documenti/informativa_studenti.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="Informativa Studente  - The document opens in new window">Informativa Studente</a></span></p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a class="application-pdf" href="https://www.uniparthenope.it/sites/default/files/informativa_orientamento_19.10.2018.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="Informativa Orientamento  - The document opens in new window" type="application/pdf; length=285722">Informativa Orientamento</a></span></p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a class="application-pdf" href="https://www.uniparthenope.it/sites/default/files/informativa_terzi_e_placement.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="Informativa Terzi e Placement  - The document opens in new window" type="application/pdf; length=248033">Informativa Terzi e Placement</a></span></p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a class="application-pdf" href="https://www.uniparthenope.it/sites/default/files/privacy/informativa_sito_web.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="Informativa Sito Web  - The document opens in new window" type="application/pdf; length=527764">Informativa Sito Web</a></span><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a href="https://www.uniparthenope.it/sites/default/files/informativa_parthenope_idem.pdf" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="  - The document opens in new window"></a></span></p> <p style="box-sizing: border-box; margin: 0px 0px 10px; color: rgb(0, 0, 0); font-family: Roboto, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 300; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); text-decoration-style: initial; text-decoration-color: initial;"><span class="icon-file fa fa-file-text-o" style="box-sizing: border-box; display: inline-block; font-style: normal; font-variant: normal; font-weight: normal; font-stretch: normal; line-height: 1; font-family: FontAwesome; font-size: inherit; text-rendering: auto; -webkit-font-smoothing: antialiased;"><a class="application-pdf" href="https://www.uniparthenope.it/sites/default/files/privacy/informativa_sito_web.pdf" rel="noopener noreferrer" style="box-sizing: border-box; background-color: transparent; color: rgb(12, 82, 153); text-decoration: underline; margin-left: 8px; font-family: Roboto, sans-serif;" target="_blank" title="informativa_sito_web.pdf  - The document opens in new window" type="application/pdf; length=527764">Informativa_sito_web.pdf</a></span></p>'

        return {'privacy': text}, 200