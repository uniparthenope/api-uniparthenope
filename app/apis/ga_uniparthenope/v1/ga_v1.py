import csv
import sys
import traceback
import urllib.request
import io

import sqlalchemy
from sqlalchemy import exc

from app import api, db
from flask_restplus import Resource, fields
from datetime import datetime, timedelta
from flask import g, request
from app.apis.uniparthenope.v1.login_v1 import token_required_general, token_required
from app.config import Config

from app.apis.ga_uniparthenope.models import Reservations

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
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Autenticazione fallita'}, g.status


# ------------- SEARCH OTHER COURSE -------------

parser = api.parser()
parser.add_argument('periodo', type=str, required=True, help='')


@ns.doc(parser=parser)
class OtherCourses(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, periodo):
        """Other Courses"""

        if g.status == 200:
            try:
                end_date = datetime.now() + timedelta(days=int(periodo) * 365 / 12)

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
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Autenticazione fallita!'}, g.status


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
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Autenticazione fallita!'}, g.status


# ------------- GET TODAY LECTURES -------------


parser = api.parser()
parser.add_argument('id_corso', required=True, help='')


@ns.doc(parser=parser)
class getTodayLecture(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, id_corso):
        """Get Today Lectures"""

        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

        #start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).timestamp()
        #end = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23, 59).timestamp()

        start = datetime(2020, 9, 21, 0, 0).timestamp()
        end = datetime(2020, 9, 21, 23, 59).timestamp()

        rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND `id_corso` = '" + str(id_corso) + "' AND start_time >= '" + str(start) + "' AND end_time <= '" + str(end) + "'")

        array = []
        for row in rs:
            array.append({
                'id': row[0],
                'start': str(datetime.fromtimestamp(row[1])),
                'end': str(datetime.fromtimestamp(row[2])),
                'room': {
                    'name': row[38],
                    'capacity': row[41]/2,
                    'description': row[40],
                    'availability': ""
                },
                'course_name': row[9],
                'prof': row[11]
            })

        print(array)

        return array, 200


# ------------- GET ALL LECTURES OF SPECIFIED COURSE -------------


parser = api.parser()
parser.add_argument('id_corso', required=True, help='')


@ns.doc(parser=parser)
class getLectures(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, id_corso):
        """Get Today Lectures"""

        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

        start = datetime.now().timestamp()

        rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id_corso = '" + str(id_corso) + "' AND E.start_time >= '" + str(start) + "' AND R.id = E.room_id")

        array = []
        for row in rs:
            array.append({
                'id': row[0],
                'start': str(datetime.fromtimestamp(row[1])),
                'end': str(datetime.fromtimestamp(row[2])),
                'room': {
                    'name': row[38],
                    'capacity': int(row[41])/2,
                    'description': row[40],
                    'availability': ""
                },
                'course_name': row[9],
                'prof': row[11]
            })

        return array, 200



# ------------- PRENOTAZIONE -------------

prenotazione = ns.model("reservation", {
    "id_corso": fields.String(description="", required=True),
    "id_lezione": fields.String(description="", required=True),
    "matricola": fields.String(description="", required=True)
})


class setReservation(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(prenotazione)
    def post(self):
        """Reservation"""
        ##TODO controllare se lo studente appartiene a quella lezione

        content = request.json

        if g.response['user']['grpId'] == 6:
            try:
                con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id = '" + content['id_lezione']  + "' AND E.room_id = R.id")
                result = rs.fetchall()
                capacity = int(result[0][41])/2
                
                r = Reservations(id_corso=content['id_corso'], username=g.response['user']['userId'], matricola=content['matricola'], time=datetime.now(), id_lezione=content['id_lezione'])
                db.session.add(r)
                
                count = Reservations.query.with_for_update().filter_by(id_lezione=content['id_lezione']).count()
                if count > capacity:
                    db.session.rollback()
                    return {
                    'errMsgTitle': 'Attenzione',
                    'errMsg': 'Raggiunta la capacità massima consentita.'
                }, 500
                
                db.session.commit()

                return {
                    "status": "Prenotazione effettuata con successo."
                }, 200

            except exc.IntegrityError:
                db.session.rollback()
                return {
                    'errMsgTitle': 'Attenzione',
                    'errMsg': 'Prenotazione già effettuata per questa lezione.'
                }, 500
            except:
                db.session.rollback()
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                    'errMsgTitle': sys.exc_info()[0].__name__,
                    'errMsg': traceback.format_exc()
                }, 500

        else:
            return {
                'errMsgTitle': "Attenzione",
                'errMsg': "Il tipo di user non è di tipo Studente"
            }, 500


# ------------- GET STUDENTS LIST -------------


parser = api.parser()
parser.add_argument('id_lezione', required=True, help='')


@ns.doc(parser=parser)
class getStudentsList(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, id_lezione):
        """Get Students Lists"""
        if g.response['user']['grpId'] == 7:
            ##TODO controllare se la lezione appartiene a quel determinato professore

            try:
                mat = Reservations.query.filter_by(id_lezione=id_lezione).all()
                
                array = []
                for m in mat:
                    array.append({
                        'matricola': m.matricola,
                        'username': m.username
                    })
                
                return array, 200
            except:
                db.session.rollback()
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                    'errMsgTitle': sys.exc_info()[0].__name__,
                    'errMsg': traceback.format_exc()
                }, 500
