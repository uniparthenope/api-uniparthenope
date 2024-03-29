import json
import sys
import traceback
import base64
import math
import requests
import sqlalchemy
from sqlalchemy import exc

from app import api, db
from flask_restplus import Resource, fields
from datetime import datetime, timedelta
from flask import g, request
from app.apis.uniparthenope.v1.login_v1 import token_required_general, token_required
from app.apis.uniparthenope.v1.professor_v1 import getCourses
from app.apis.uniparthenope.v2.students_v2 import MyExams
from app.config import Config

from app.apis.ga_uniparthenope.models import Reservations, ReservableRoom, Room, Area, Entry, UserTemp
from app.apis.access.models import UserAccess

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
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


# ------------- GET TODAY SERVICES -------------


class getTodayServices(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get Today Services"""
        if g.status == 200:
            username = g.response['user']['userId']

            array = []

            try:
                start = datetime.now().date()
                end = start + timedelta(days=2)

                grpid = "," + str(g.response['user']['grpId']) + ","

                aree = Area.query.all()
                for area in aree:
                    array_area = []
                    service = []

                    services = db.session.query(Entry, Room).filter(Room.id == Entry.room_id) \
                        .filter(Entry.start_time >= start) \
                        .filter(Entry.end_time <= end) \
                        .filter(Entry.end_time > datetime.now()) \
                        .filter(Room.area_id == area.id) \
                        .filter(Room.user_access.contains(grpid))

                    for s in services:
                        reserved = False
                        resered_id = None
                        reserved_by = None
                        reservation = Reservations.query.filter_by(id_lezione=s.Entry.id).filter_by(
                            username=username)

                        if reservation.first() is not None:
                            reserved = True
                            resered_id = reservation.first().id
                            reserved_by = reservation.first().reserved_by

                        if s.Room.piano is None or s.Room.piano == '999':
                            piano = " "
                        else:
                            piano = s.Room.piano
                        if s.Room.lato is None:
                            lato = " "
                        else:
                            lato = s.Room.lato

                        service.append({
                            'id': s.Entry.id,
                            'start': str(s.Entry.start_time),
                            'end': str(s.Entry.end_time),
                            'room': {
                                'name': s.Room.room_name,
                                'capacity': math.floor(s.Room.capacity / int(Config.CAPACITY_F)),
                                'description': "Piano " + piano + " Lato " + lato,
                                'availability': math.floor(
                                    s.Room.capacity / int(Config.CAPACITY_F)) - Reservations.query.with_for_update().filter_by(
                                    id_lezione=s.Entry.id).count()
                            },
                            'reservation': {
                                'reserved_id': resered_id,
                                'reserved': reserved,
                                'reserved_by': reserved_by
                            }
                        })

                    array.append({
                        'area': area.area_name,
                        'services': service
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

        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET TODAY LECTURES -------------


parser = api.parser()
parser.add_argument('matId', required=True, help='')


@ns.doc(parser=parser)
class getTodayLecture(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId):
        """Get Today Lectures"""

        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        result = MyExams(Resource).get(matId)

        status = json.loads(json.dumps(result))[1]
        _result = json.loads(json.dumps(result))[0]

        if status == 200:
            codici = []
            codici_res = []

            for i in range(len(_result)):
                if _result[i]['status']['esito'] == 'P' or _result[i]['status']['esito'] == 'F':
                    codici.append(_result[i]['codice'])

            res = Reservations.query.filter_by(username=username)
            for r in res:
                if r.id_corso not in codici:
                    codici.append(r.id_corso)

            array = []
            start = datetime.now().date()
            end = start + timedelta(days=1)

            for i in range(len(codici)):
                codice = codici[i]
                rs = con.execute(
                    "SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND `id_corso` LIKE '%%" + str(
                        codice) + "%%' AND start_time >= '" + str(start) + "' AND end_time <= '" + str(end) + "'")

                for row in rs:
                    reserved = False
                    resered_id = None
                    reserved_by = None
                    reservation = Reservations.query.filter_by(id_lezione=row[0]).filter_by(
                        username=username)

                    if reservation.first() is not None:
                        reserved = True
                        resered_id = reservation.first().id
                        reserved_by = reservation.first().reserved_by

                    array.append({
                        'id': row[0],
                        'id_corso': codice,
                        'start': str(datetime.fromtimestamp(row[1])),
                        'end': str(datetime.fromtimestamp(row[2])),
                        'room': {
                            'name': row[38],
                            'capacity': math.floor(row[41] / int(Config.CAPACITY_F)),
                            'description': row[40],
                            'availability': math.floor(
                                int(row[41]) / int(Config.CAPACITY_F)) - Reservations.query.with_for_update().filter_by(
                                id_lezione=row[0]).count()
                        },
                        'course_name': row[9],
                        'prof': row[11],
                        'reservation': {
                            'reserved_id': resered_id,
                            'reserved': reserved,
                            'reserved_by': reserved_by
                        }
                    })

            return array, 200

        else:
            return {'errMsg': _result['errMsg']}, status


# ------------- GET ALL OWN LECTURES -------------


parser = api.parser()
parser.add_argument('matId', required=True, help='')


@ns.doc(parser=parser)
class getLectures(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, matId):
        """Get All Own Lectures"""
        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        result = MyExams(Resource).get(matId)

        status = json.loads(json.dumps(result))[1]
        _result = json.loads(json.dumps(result))[0]

        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

        start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).timestamp()

        if status == 200:
            array = []

            for i in range(len(_result)):
                if _result[i]['status']['esito'] == 'P' or _result[i]['status']['esito'] == 'F':
                    codice = _result[i]['codice']

                    rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id_corso LIKE '%%" + str(
                        codice) + "%%' AND E.start_time >= '" + str(start) + "' AND R.id = E.room_id")

                    for row in rs:
                        reserved = False
                        resered_id = None
                        reserved_by = None
                        reservation = Reservations.query.filter_by(id_lezione=row[0]).filter_by(
                            username=username)

                        if reservation.first() is not None:
                            reserved = True
                            resered_id = reservation.first().id
                            reserved_by = reservation.first().reserved_by

                        array.append({
                            'id': row[0],
                            'id_corso': codice,
                            'start': str(datetime.fromtimestamp(row[1])),
                            'end': str(datetime.fromtimestamp(row[2])),
                            'room': {
                                'name': row[38],
                                'capacity': math.floor(int(row[41]) / int(Config.CAPACITY_F)),
                                'description': row[40],
                                'availability': math.floor(
                                    int(row[41]) / int(Config.CAPACITY_F)) - Reservations.query.with_for_update().filter_by(
                                    id_lezione=row[0]).count()
                            },
                            'course_name': row[9],
                            'prof': row[11],
                            'reservation': {
                                'reserved_id': resered_id,
                                'reserved': reserved,
                                'reserved_by': reserved_by
                            }
                        })

            res = Reservations.query.filter_by(username=username).filter(
                Reservations.start_time >= datetime.fromtimestamp(start)).all()

            if len(array) == 0:
                for r in res:
                    rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id ='" + str(
                        r.id_lezione) + "' AND E.start_time >= '" + str(start) + "' AND R.id = E.room_id")
                    for row in rs:
                        array.append({
                            'id': row[0],
                            'id_corso': r.id_corso,
                            'start': str(datetime.fromtimestamp(row[1])),
                            'end': str(datetime.fromtimestamp(row[2])),
                            'room': {
                                'name': row[38],
                                'capacity': math.floor(int(row[41]) / int(Config.CAPACITY_F)),
                                'description': row[40],
                                'availability': math.floor(
                                    int(row[41]) / int(Config.CAPACITY_F)) - Reservations.query.with_for_update().filter_by(
                                    id_lezione=row[0]).count()
                            },
                            'course_name': row[9],
                            'prof': row[11],
                            'reservation': {
                                'reserved_id': r.id,
                                'reserved': True,
                                'reserved_by': r.reserved_by
                            }
                        })
            else:
                id_lez = []
                for i in range(len(array)):
                    id_lez.append(array[i]['id'])

                print(id_lez)
                for r in res:
                    if r.id_lezione not in id_lez:
                        rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id ='" + str(
                            r.id_lezione) + "' AND E.start_time >= '" + str(start) + "' AND R.id = E.room_id")
                        for row in rs:
                            array.append({
                                'id': row[0],
                                'id_corso': r.id_corso,
                                'start': str(datetime.fromtimestamp(row[1])),
                                'end': str(datetime.fromtimestamp(row[2])),
                                'room': {
                                    'name': row[38],
                                    'capacity': math.floor(int(row[41]) / int(Config.CAPACITY_F)),
                                    'description': row[40],
                                    'availability': math.floor(
                                        int(row[41]) / int(Config.CAPACITY_F)) - Reservations.query.with_for_update().filter_by(
                                        id_lezione=row[0]).count()
                                },
                                'course_name': row[9],
                                'prof': row[11],
                                'reservation': {
                                    'reserved_id': r.id,
                                    'reserved': True,
                                    'reserved_by': r.reserved_by
                                }
                            })

            return array, 200
        else:
            return {'errMsg': _result['errMsg']}, status


# ------------- GET ALL PROF LECTURES -------------


parser = api.parser()
parser.add_argument('aaId', required=True, help='')


@ns.doc(parser=parser)
class getProfLectures(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self, aaId):
        """Get All Prof Lectures"""
        result = getCourses(Resource).get(aaId)

        status = json.loads(json.dumps(result))[1]
        _result = json.loads(json.dumps(result))[0]

        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

        if status == 200:
            base64_bytes = g.token.encode('utf-8')
            message_bytes = base64.b64decode(base64_bytes)
            token_string = message_bytes.decode('utf-8')

            username = token_string.split(':')[0]

            array = []

            for i in range(len(_result)):
                codice = _result[i]['adDefAppCod']

                start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).timestamp()

                rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id_corso LIKE '%%" + str(
                    codice) + "%%' AND E.start_time >= '" + str(start) + "' AND R.id = E.room_id")
                # COGNOMI CON SPAZI E ACCENTI
                # AND E.description LIKE '%%" + username.split(".")[1] + "%%'")

                courses = []
                for row in rs:
                    courses.append({
                        'id': row[0],
                        'start': str(datetime.fromtimestamp(row[1])),
                        'end': str(datetime.fromtimestamp(row[2])),
                        'room': {
                            'name': row[38],
                            'capacity': math.floor(int(row[41]) / int(Config.CAPACITY_F)),
                            'description': row[40],
                            'availability': math.floor(
                                int(row[41]) / int(Config.CAPACITY_F)) - Reservations.query.with_for_update().filter_by(
                                id_lezione=row[0]).count()
                        },
                        'course_name': row[9],
                        'prof': row[11]
                    })
                array.append({
                    'nome': _result[i]['adDes'],
                    'courses': courses
                })

            # print(array)
            return array, 200
        else:
            return {'errMsg': _result['errMsg']}, status


# ------------- SERVICES RESERVATIONS -------------
prenotazione_servizi = ns.model("services_reservation", {
    "id_entry": fields.String(description="", required=True),
    "matricola": fields.String(description="", required=True)
})


def reserve(username, content, rs):
    try:
        capacity = math.floor(rs.Room.capacity / int(Config.CAPACITY_F))

        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)

        if rs.Entry.start_time > now or rs.Entry.end_time > now or rs.Entry.end_time < datetime.now():
            return {
                       'errMsgTitle': 'Attenzione',
                       'errMsg': 'Prenotazione non consentita.'
                   }, 500

        start = datetime.now().date()
        end = start + timedelta(days=2)

        today_reservations = Reservations.query.filter_by(username=username).filter(
            Reservations.start_time >= start).filter(
            Reservations.end_time <= end).all()

        for res in today_reservations:
            if res.start_time <= rs.Entry.start_time < res.end_time or res.start_time < rs.Entry.end_time <= res.end_time:
                return {
                           'errMsgTitle': 'Attenzione',
                           'errMsg': 'Già presente una prenotazione in questo lasso di tempo.'
                       }, 500

        r = Reservations(id_corso="SERVICE", course_name=rs.Entry.name,
                         start_time=rs.Entry.start_time,
                         end_time=rs.Entry.end_time,
                         username=username, matricola=content['matricola'],
                         time=datetime.now(), id_lezione=content['id_entry'],
                         reserved_by=username)
        db.session.add(r)

        count = Reservations.query.with_for_update().filter_by(
            id_lezione=content['id_entry']).count()
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
                   'errMsg': 'Prenotazione già effettuata per questo servizio.'
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


class ServicesReservation(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(prenotazione_servizi)
    def post(self):
        """Set Service Reservation"""
        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        content = request.json
        if g.status == 200 and 'id_entry' in content and 'matricola' in content:
            rs = db.session.query(Entry, Room).filter(Room.id == Entry.room_id).filter(
                Entry.id == content['id_entry']).first()
            grpid = "," + str(g.response['user']['grpId']) + ","

            if grpid in rs.Room.user_access:
                if g.response['user']['grpId'] != 7 and g.response['user']['grpId'] != 99:
                    user = UserAccess.query.filter_by(username=username).first()
                    if user is not None and user.greenpass:
                        return reserve(username, content, rs)
                    else:
                        return {'status': 'error',
                                'errMsg': 'Impossibile prenotarsi in mancanza di Green Pass.'}, 500

                else:
                    return reserve(username, content, rs)

            else:
                return {
                           'errMsgTitle': 'Attenzione',
                           'errMsg': 'Utente non autorizzato per questo servizio.'
                       }, 500
        else:
            return {'errMsg': 'Errore username/pass!'}, g.status


# ------------- RESERVATIONS -------------
prenotazione = ns.model("reservation", {
    "id_corso": fields.String(description="", required=True),
    "id_lezione": fields.String(description="", required=True),
    "matricola": fields.String(description="", required=True),
    "matId": fields.String(description="", required=True)
})


class Reservation(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    @ns.expect(prenotazione)
    def post(self):
        """Set Reservation"""
        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        content = request.json
        if 'id_corso' in content and 'id_lezione' in content and 'matricola' in content and 'matId' in content:

            result = MyExams(Resource).get(content['matId'])

            status = json.loads(json.dumps(result))[1]
            _result = json.loads(json.dumps(result))[0]

            codici = []
            if status == 200:
                for i in range(len(_result)):
                    if _result[i]['status']['esito'] == 'P' or _result[i]['status']['esito'] == 'F':
                        codici.append(_result[i]['codice'])

                codici_res = []

                res_room = ReservableRoom.query.all()
                for rr in res_room:
                    codici_res.append(rr.id_corso)

                try:
                    user_info = UserTemp.query.filter_by(username=username).first()
                    if content['id_corso'] in codici or user_info is not None:
                        user = UserAccess.query.filter_by(username=username).first()
                        if user is not None:
                            if user.autocertification and user.classroom == "presence":
                                con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                                rs = con.execute(
                                    "SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id = '" + content[
                                        'id_lezione'] + "' AND E.room_id = R.id")
                                result = rs.fetchall()
                                capacity = int(result[0][41]) / int(Config.CAPACITY_F)

                                now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
                                    days=1)

                                if datetime.fromtimestamp(result[0][1]) > now or datetime.fromtimestamp(
                                        result[0][2]) > now or datetime.fromtimestamp(result[0][2]) < datetime.now():
                                    return {
                                               'errMsgTitle': 'Attenzione',
                                               'errMsg': 'Prenotazione non consentita.'
                                           }, 500
                                start = datetime.now().date()
                                end = start + timedelta(days=1)

                                today_reservations = Reservations.query.filter_by(username=username).filter(
                                    Reservations.start_time >= start).filter(
                                    Reservations.end_time <= end).all()

                                for res in today_reservations:
                                    if res.start_time <= datetime.fromtimestamp(
                                            result[0][1]) < res.end_time or res.start_time < datetime.fromtimestamp(
                                            result[0][2]) <= res.end_time:
                                        return {
                                                   'errMsgTitle': 'Attenzione',
                                                   'errMsg': 'Già presente una prenotazione in questo lasso di tempo.'
                                               }, 500

                                r = Reservations(id_corso=content['id_corso'], course_name=result[0][9],
                                                 start_time=datetime.fromtimestamp(result[0][1]),
                                                 end_time=datetime.fromtimestamp(result[0][2]),
                                                 username=username, matricola=content['matricola'],
                                                 time=datetime.now(), id_lezione=content['id_lezione'],
                                                 reserved_by=username)
                                db.session.add(r)

                                count = Reservations.query.with_for_update().filter_by(
                                    id_lezione=content['id_lezione']).count()
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
                            else:
                                return {'status': 'error',
                                        'errMsg': 'Impossibile prenotarsi in mancanza di autocertificazione/accesso in presenza.'}, 500
                        else:
                            return {'status': 'error',
                                    'errMsg': 'Impossibile prenotarsi in mancanza di autocertificazione/accesso in presenza.'}, 500
                    else:
                        return {
                                   'errMsgTitle': 'Attenzione',
                                   'errMsg': 'Non è possibile prenotarsi ad una lezione non presente nel proprio piano di studi/già superata.'
                               }, 500

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
                return {'errMsg': _result['errMsg']}, status
        else:
            return {'errMsg': 'Payload error!'}, 500

    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get Reservations"""
        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        if g.status == 200:
            if g.response['user']['grpId'] == 6:
                try:
                    start = datetime.now().date()
                    end = start + timedelta(days=1)

                    reservations = Reservations.query.filter_by(username=username).filter(
                        Reservations.start_time >= datetime.fromtimestamp(start)).all()
                    array = []
                    for r in reservations:
                        array.append({
                            "id": r.id,
                            "id_corso": r.id_corso,
                            "course_name": r.course_name,
                            "start_time": str(r.start_time),
                            "end_time": str(r.end_time),
                            'reserved_by': r.reserved_by
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

            else:
                return {
                           'errMsgTitle': "Attenzione",
                           'errMsg': "Il tipo di user non è di tipo Studente"
                       }, 500

        else:
            return {'errMsg': 'Wrong username/pass'}, g.status

    @ns.doc(security='Basic Auth')
    @token_required_general
    def delete(self, id_prenotazione):
        """Delete Reservation"""
        if g.status == 200:
            base64_bytes = g.token.encode('utf-8')
            message_bytes = base64.b64decode(base64_bytes)
            token_string = message_bytes.decode('utf-8')

            username = token_string.split(':')[0]

            #TODO creare funzione per cancellare dal db
            if g.response['user']['grpId'] == 7:
                try:
                    reservation = Reservations.query.filter_by(id=id_prenotazione)

                    if reservation.first() is not None:
                        reservation.delete()
                        db.session.commit()

                        return {
                                   "status": "Cancellazione effettuata con successo."
                               }, 200
                    else:
                        return {
                                   'errMsgTitle': "Attenzione",
                                   'errMsg': "Operazione non consentita."
                               }, 500

                except AttributeError as error:
                    return {
                               'errMsgTitle': "Attenzione",
                               'errMsg': "Operazione non consentita."
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

            elif g.response['user']['grpId'] == 101:
                try:
                    reservation = Reservations.query.filter_by(id=id_prenotazione).first()
                    id_lezione = reservation.id_lezione
                    if id_lezione is not None:
                        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                        rs = con.execute("SELECT * FROM `mrbs_entry` WHERE id = '" + id_lezione + "'")
                        for row in rs:
                            if row[10] == 'J':
                                reservation.delete()
                                db.session.commit()

                                con.dispose()

                                return {
                                   "status": "Cancellazione effettuata con successo."
                               }, 200
                            else:
                                 return {
                                    'errMsgTitle': "Attenzione",
                                    'errMsg': "Operazione non consentita."
                                }, 500
                    else:
                        return {
                            'errMsgTitle': "Attenzione",
                            'errMsg': "Operazione non consentita."
                        }, 500
                except AttributeError as error:
                    return {
                               'errMsgTitle': "Attenzione",
                               'errMsg': "Operazione non consentita."
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
                try:
                    reservation = Reservations.query.filter_by(id=id_prenotazione).filter_by(
                        username=username)

                    if reservation.first() is not None:
                        reservation.delete()
                        db.session.commit()

                        return {
                                   "status": "Cancellazione effettuata con successo."
                               }, 200
                    else:
                        return {
                                   'errMsgTitle': "Attenzione",
                                   'errMsg': "Operazione non consentita."
                               }, 500

                except AttributeError as error:
                    return {
                               'errMsgTitle': "Attenzione",
                               'errMsg': "Operazione non consentita."
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
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- RESERVE STUDENT BY PROF -------------
prenotazione_prof = ns.model("reservation_prof", {
    "id_lezione": fields.String(description="", required=True),
    "matricola": fields.String(description="", required=True),
    "username": fields.String(description="", required=True),
    "aaId": fields.String(description="", required=True)
})


class ReservationByProf(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(prenotazione_prof)
    def post(self):
        """Set Reservation to student"""
        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        content = request.json

        if 'id_lezione' in content and 'matricola' in content and 'username' in content and 'aaId' in content:
            if g.response['user']['grpId'] == 7:
                con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN mrbs_room R WHERE E.id = '" + str(
                        content['id_lezione']) + "' AND E.room_id = R.id").fetchall()
                capacity = math.floor(int(rs[0][41]) / int(Config.CAPACITY_F))

                if len(rs) != 0:
                    r = Reservations(id_corso=rs[0][32], course_name=rs[0][9],
                                start_time=datetime.fromtimestamp(rs[0][1]),
                                end_time=datetime.fromtimestamp(rs[0][2]),
                                username=content['username'], matricola=content['matricola'],
                                time=datetime.now(), id_lezione=content['id_lezione'],
                                reserved_by=username)
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
                else:
                    return {
                            'errMsgTitle': "Attenzione",
                            'errMsg': "ID lezione errato"
                    }, 500
            else:
                return {
                        'errMsgTitle': "Attenzione",
                        'errMsg': "Operazione non consentita!"
                }, 500
        else:
            return {
                    'errMsgTitle': "Attenzione",
                    'errMsg': "Errore Payload/Studente non immatricolato!"
            }, 500


    #TODO Funzione futura
    '''
    def post(self):
        """Set Reservation to student"""
        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')

        username = token_string.split(':')[0]

        content = request.json
        print(content)

        if 'id_lezione' in content and 'matricola' in content and 'username' in content and 'aaId' in content:

            result = getCourses(Resource).get(content['aaId'])

            status = json.loads(json.dumps(result))[1]
            _result = json.loads(json.dumps(result))[0]

            if status == 200:
                try:
                    codici = []
                    for i in range(len(_result)):
                        codici.append(_result[i]['adDefAppCod'])

                    con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                    rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN mrbs_room R WHERE E.id = '" + str(
                        content['id_lezione']) + "' AND E.room_id = R.id").fetchall()
                    capacity = int(rs[0][41]) / 2
                    if len(rs) != 0:
                        if rs[0][32] in codici:
                            r = Reservations(id_corso=rs[0][32], course_name=rs[0][9],
                                             start_time=datetime.fromtimestamp(rs[0][1]),
                                             end_time=datetime.fromtimestamp(rs[0][2]),
                                             username=content['username'], matricola=content['matricola'],
                                             time=datetime.now(), id_lezione=content['id_lezione'],
                                             reserved_by=username)
                            db.session.add(r)

                            count = Reservations.query.with_for_update().filter_by(
                                id_lezione=content['id_lezione']).count()
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
                        else:
                            return {
                                       'errMsgTitle': "Attenzione",
                                       'errMsg': "Operazione non consentita!"
                                   }, 500
                    else:
                        return {
                                   'errMsgTitle': "Attenzione",
                                   'errMsg': "ID lezione errato"
                               }, 500

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
                           'errMsg': "Errore nel caricamento degli esami!!"
                       }, 500

        else:
            return {
                       'errMsgTitle': "Attenzione",
                       'errMsg': "Errore Payload/Studente non immatricolato!"
                   }, 500
    '''


# ------------- GET STUDENTS LIST -------------


parser = api.parser()
parser.add_argument('id_lezione', required=True, help='')

import concurrent.futures
from functools import partial

def get_info(row):
    try:
        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + Config.USER_ROOT
        }

        response = requests.request("GET", url + "anagrafica-service-v2/utenti/" + row.username, headers=headers, timeout=10)
        _response = response.json()

        if response.status_code == 200:
            persId = str(_response[0]['persId'])
            response = requests.request("GET", url + "anagrafica-service-v2/persone/" + persId, headers=headers, timeout=10)
            _response = response.json()
            return {
                'id': row.id,
                'matricola': row.matricola,
                'username': row.username,
                'email': _response["emailAte"]
            }
        else:
            return "--"
    except:
        print("Unexpected error:")
        print("Title: " + sys.exc_info()[0].__name__)
        print("Description: " + traceback.format_exc())
        return "--"


def get_students_list(id_lezione):
    mat = Reservations.query.filter_by(id_lezione=id_lezione).all()
    
    array = []

    workers = 30
    func = partial(get_info)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(func, mat):
            array.append(result)

    return array


@ns.doc(parser=parser)
class getStudentsList(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, id_lezione):
        """Get Students Lists"""
        if g.status == 200:
            if g.response['user']['grpId'] == 7:
                ##TODO controllare se la lezione appartiene a quel determinato professore

                try:
                    array = get_students_list(id_lezione)

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
            elif g.response['user']['grpId'] == 101:
                try:
                    con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                    rs = con.execute("SELECT * FROM `mrbs_entry` WHERE id = '" + id_lezione + "'")
                    
                    for row in rs:
                        if row[10] == 'J':
                            array = get_students_list(id_lezione)

                            con.dispose()

                            return array, 200
                        else:
                            return {
                                'errMsgTitle': "Attenzione",
                                'errMsg': "Il tipo di utente non è abilitato a visualizzare la lista degli studenti!"
                            }, 500
                    con.dispose()
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
                           'errMsg': "Il tipo di user non è di tipo Docente"
                       }, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET EVENTS -------------


class getEvents(Resource):
    def get(self):
        """Get Events"""
        try:
            start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).timestamp()
            con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
            rs = con.execute(
                "SELECT *  FROM `mrbs_entry` E JOIN mrbs_room R WHERE (E.type = 't' COLLATE utf8mb4_bin OR E.type = 's' COLLATE utf8mb4_bin OR E.type = 'b' COLLATE utf8mb4_bin OR E.type = 'a' COLLATE utf8mb4_bin OR E.type = 'z' COLLATE utf8mb4_bin OR E.type = 'Y' COLLATE utf8mb4_bin OR E.type = 'O' COLLATE utf8mb4_bin) AND start_time >= '" + str(
                    start) + "' AND E.room_id = R.id")

            array = []
            for row in rs:
                array.append({
                    'id': row[0],
                    'start': str(datetime.fromtimestamp(row[1])),
                    'end': str(datetime.fromtimestamp(row[2])),
                    'room': {
                        'name': row[38],
                        'capacity': int(row[41]) / int(Config.CAPACITY_F),
                        'description': row[40],
                        'availability': int(row[41]) / int(Config.CAPACITY_F) - Reservations.query.with_for_update().filter_by(
                            id_lezione=row[0]).count()
                    },
                    'course_name': row[9],
                    'description': row[11],
                    'type': row[10]
                })

            return array, 200

        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500
