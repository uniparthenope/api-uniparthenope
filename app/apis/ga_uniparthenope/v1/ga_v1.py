import csv
import urllib.request
import io
from app import api
from flask_restplus import Resource
from datetime import datetime, timedelta
from flask import g
from app.apis.uniparthenope.v1.login_v1 import token_required_general

ns = api.namespace('uniparthenope')


# ------------- GLOBAL FUNCTIONS -------------

def createDate(data):
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
            "ottobre", "novembre", "dicembre"]
    data = data.split()
    # print(data)
    ora = data[0][0:2]
    minuti = data[0][3:5]
    anno = data[5]
    giorno = data[3]
    mese = mesi.index(data[4]) + 1

    # final_data = datetime(anno, mese, giorno, ora, minuti)
    final_data = str(anno) + "/" + str(mese) + "/" + str(giorno) + " " + str(ora) + ":" + str(minuti)
    return final_data


def extractData(data):
    data_split = data.split()[0]
    export_data = datetime.strptime(data_split, '%d/%m/%Y')

    return export_data


# ------------- SEARCH COURSE -------------

parser = api.parser()
parser.add_argument('nome_area', type=str, required=True, help='Area name')
parser.add_argument('nome_corso', type=str, required=True, help='')
parser.add_argument('nome_prof', type=str, required=True, help='')
parser.add_argument('nome_studio', type=str, required=True, help='')
parser.add_argument('periodo', type=str, required=True, help='')


@ns.doc(parser=parser)
class SearchCourse(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, nome_area, nome_corso, nome_prof, nome_studio, periodo):
        """Search course"""

        array = []

        end_date = datetime.now() + timedelta(days=int(periodo) * 365 / 12)
        area = nome_area.replace(" ", "+")

        if g.status == 200:
            try:
                url_n = 'http://ga.uniparthenope.it/report.php?from_day=' + str(datetime.now().day) + \
                        '&from_month=' + str(datetime.now().month) + \
                        '&from_year=' + str(datetime.now().year) + \
                        '&to_day=' + str(end_date.day) + \
                        '&to_month=' + str(end_date.month) + \
                        '&to_year=' + str(end_date.year) + \
                        '&areamatch=' + area + \
                        '&roommatch=&typematch%5B%5D=' + nome_studio + \
                        '&namematch=&descrmatch=&creatormatch=&match_private=0&match_confirmed=1&match_referente=&match_unita_interne=&match_ore_unita_interne=&match_unita_vigilanza=&match_ore_unita_vigilanza=&match_unita_pulizie=&match_ore_unita_pulizie=&match_audio_video=&match_catering=&match_Acconto=&match_Saldo=&match_Fattura=&output=0&output_format=1&sortby=s&sumby=d&phase=2&datatable=1'

                url_open = urllib.request.urlopen(url_n)
                csvfile = csv.reader(io.StringIO(url_open.read().decode('utf-16')), delimiter=',')

                for row in csvfile:
                    index = 0
                    prof = 0

                    for w in row:
                        if (w.find(nome_prof)) != -1:
                            prof = index
                        index += 1

                    for word in nome_corso:
                        item = {}
                        if row[0].find(word) != -1 and prof != 0:
                            item.update({'aula': row[2]})
                            item.update({'inizio': createDate(row[3])})
                            item.update({'fine': createDate(row[4])})
                            item.update({'tot': row[5]})
                            item.update({'docente': row[prof]})
                            break

                    if item:
                        array.append(item)
                if array:
                    print(array)
                    return array, 200
            except:
                return {'errMsg': 'generic error'}, 500
        else:
            return {'errMsg': 'generic error'}, g.status


# ------------- SEARCH OTHER COURSE -------------

parser = api.parser()
parser.add_argument('periodo', type=str, required=True, help='')


@ns.doc(parser=parser)
class OtherCourses(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, periodo):
        """Other Courses"""

        end_date = datetime.now() + timedelta(days=int(periodo) * 365 / 12)

        if g.status == 200:
            try:
                url_n = 'http://ga.uniparthenope.it/report.php?from_day=' + str(datetime.now().day) + \
                        '&from_month=' + str(datetime.now().month) + \
                        '&from_year=' + str(datetime.now().year) + \
                        '&to_day=' + str(end_date.day) + \
                        '&to_month=' + str(end_date.month) + \
                        '&to_year=' + str(end_date.year) + \
                        '&areamatch=Centro+Direzionale&roommatch=&typematch%5B%5D=O&typematch%5B%5D=Y&typematch%5B%5D=Z&typematch%5B%5D=a&typematch%5B%5D=b&typematch%5B%5D=c&typematch%5B%5D=s&typematch%5B%5D=t' + \
                        '&namematch=&descrmatch=&creatormatch=&match_private=0&match_confirmed=1&match_referente=&match_unita_interne=&match_ore_unita_interne=&match_unita_vigilanza=&match_ore_unita_vigilanza=&match_unita_pulizie=&match_ore_unita_pulizie=&match_audio_video=&match_catering=&match_Acconto=&match_Saldo=&match_Fattura=&output=0&output_format=1&sortby=s&sumby=d&phase=2&datatable=1'
                url_open = urllib.request.urlopen(url_n)
                csvfile = csv.reader(io.StringIO(url_open.read().decode('utf-16')), delimiter=',')

                array = []
                next(csvfile)
                for row in csvfile:
                    lower = row[6].lower()
                    if lower.find("manutenzione") != -1:
                        id = "M"
                    else:
                        id = row[7]
                    item = ({
                        'titolo': row[0],
                        'aula': row[2],
                        'start_time': createDate(row[3]),
                        'end_time': createDate(row[4]),
                        'durata': row[5],
                        'descrizione': row[6],
                        'id': id,
                        'confermato': row[9]
                    })
                    array.append(item)

                return array, 200
            except:
                return {'errMsg': 'generic error'}, 500
        else:
            return {'errMsg': 'generic error'}, g.status


# ------------- SEARCH BY NAME AND SURNAME -------------


parser = api.parser()
parser.add_argument('periodo', type=str, required=True, help='')
parser.add_argument('cognome', type=str, required=True, help='')


@ns.doc(parser=parser)
class ProfessorCourse(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, periodo, cognome):
        """Other Courses"""

        end_date = datetime.now() + timedelta(days=int(periodo) * 365 / 12)
        cognome = cognome.replace(" ", "+")

        if g.status == 200:
            try:
                url_n = 'http://ga.uniparthenope.it/report.php?from_day=' + str(datetime.now().day) + \
                        '&from_month=' + str(datetime.now().month) + \
                        '&from_year=' + str(datetime.now().year) + \
                        '&to_day=' + str(end_date.day) + \
                        '&to_month=' + str(end_date.month) + \
                        '&to_year=' + str(end_date.year) + \
                        '&areamatch=&roommatch=' + \
                        '&namematch=&descrmatch=' + cognome + \
                        '&creatormatch=&match_private=0&match_confirmed=2&match_referente=&match_unita_interne=&match_ore_unita_interne=&match_unita_vigilanza=&match_ore_unita_vigilanza=&match_unita_pulizie=&match_ore_unita_pulizie=&match_audio_video=&match_catering=&match_Acconto=&match_Saldo=&match_Fattura=' + \
                        '&output=0&output_format=1&sortby=s&sumby=d&phase=2&datatable=1'
                url_open = urllib.request.urlopen(url_n)
                csvfile = csv.reader(io.StringIO(url_open.read().decode('utf-16')), delimiter=',')

                array = []
                next(csvfile)
                for row in csvfile:


                    lower = row[6].lower()
                    if lower.find("manutenzione") != -1:
                        id = "M"
                    else:
                        id = row[7]
                    item = ({
                        'titolo': row[0],
                        'aula': row[2],
                        'start_time': createDate(row[3]),
                        'end_time': createDate(row[4]),
                        'durata': row[5],
                        'descrizione': row[6],
                        'id': id,
                        'confermato': row[9]
                    })
                    array.append(item)

                return array, 200
            except:
                return {'errMsg': 'generic error'}, 500
        else:
            return {'errMsg': 'generic error'}, g.status