import sys
import traceback

import sqlalchemy
from datetime import datetime, timedelta
import math

from sqlalchemy import exc

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.config import Config

from app.apis.ga_uniparthenope.models import Reservations, Area, Room, GaTypes
from app.models import User, Role

from flask_restplus import Resource, fields
from flask import g, request

ns = api.namespace('uniparthenope')


# ------------- GET ALL TODAY CLASSROOMS -------------


class getAllTodayRooms(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get ALl Today Rooms"""
        if g.status == 200:
            username = g.response['user']['userId']

            areas = []

            all_areas = Area.query.all()
            for area in all_areas:
                areas.append({'area': area.area_name, 'services': []})

            _now = datetime.now() + timedelta(hours=6)
            start = _now.replace(hour=18, minute=0, second=0, microsecond=0)
            start = start - timedelta(days=1)
            
            end = _now.replace(hour=18, minute=0, second=0, microsecond=0)
            end = end + timedelta(days=2)
            
            # print("Start: ",start)
            # print("End: ", end)
            
            start = start.timestamp()
            end = end.timestamp()

            con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

            rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND ((start_time >= '" + str(datetime.now().timestamp()) + "' AND BINARY type = 'J')  OR (start_time >= '" + str(start) + "' AND end_time <= '" + str(end) + "' AND BINARY type != 'W' AND BINARY type != 'c' AND BINARY type != 'b' AND BINARY type != 't' AND BINARY type != 'O'))")

            for row in rs:
                reserved = False
                resered_id = None
                reserved_by = None
                #reservation = Reservations.query.filter_by(id_lezione=row[0]).filter_by(username=username)
                _reservation = Reservations.query.filter_by(id_lezione=row[0])
                reservation = _reservation.filter_by(username=username)
                res_count = _reservation.count()

                if reservation.first() is not None:
                    reserved = True
                    resered_id = reservation.first().id
                    reserved_by = reservation.first().reserved_by


                capacity = math.floor(int(row[41]) / int(Config.CAPACITY_F))

                areas[row[37] - 1]['services'].append({
                    'id': row[0],
                    'id_corso': row[32],
                    'start': str(datetime.fromtimestamp(row[1])),
                    'end': str(datetime.fromtimestamp(row[2])),
                    'room': {
                        'name': row[38],
                        'capacity': capacity,
                        'description': row[40],
                        'availability': capacity - res_count
                    },
                    'course_name': row[9],
                    'prof': row[11],
                    'reservation': {
                        'reserved_id': resered_id,
                        'reserved': reserved,
                        'reserved_by': reserved_by
                    }
                })
            con.dispose()
            sorted_areas = []
            for a in areas:
                #if 'Teams' not in a['area']:
                sorted_s = sorted(a['services'], key=lambda k: k['course_name'])
                sorted_areas.append({
                    'area': a['area'],
                    'services': sorted_s
                })
            #sorted_areas = sorted(areas, key=lambda k: k['course_name'])
            return sorted_areas, 200
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- CLASSROOMS RESERVATIONS -------------


prenotazione_aule = ns.model("services_reservation", {
    "id_lezione": fields.String(description="", required=True),
    "matricola": fields.String(description="", required=True),
    "id_corso": fields.String(description="", required=True)
})


class RoomsReservation(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(prenotazione_aule)
    def post(self):
        """Set Rooms Reservation"""
        content = request.json

        if 'id_lezione' in content and 'matricola' in content and 'id_corso' in content:
            if g.status == 200:
                if g.response['user']['grpId'] != 7 and g.response['user']['grpId'] != 99:
                    try:
                        username = g.response['user']['userId']
                        #print(username)

                        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                        rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id = '" + content[
                            'id_lezione'] + "' AND E.room_id = R.id")

                        result = rs.fetchall()
                        capacity = int(result[0][41]) / int(Config.CAPACITY_F)

                        #start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        #end = start + timedelta(days=3)
                        _now = datetime.now() + timedelta(hours=6)
                        start = _now.replace(hour=18, minute=0, second=0, microsecond=0)
                        start = start - timedelta(days=1)

                        end = _now.replace(hour=18, minute=0, second=0, microsecond=0)
                        end = end + timedelta(days=2)

                        if int(content['id_lezione']) in Config.ACCENTURE_LECTIONS:
                            start = datetime.fromtimestamp(result[0][1])
                            end = datetime.fromtimestamp(result[0][2])

                        elif datetime.fromtimestamp(result[0][1]) < start or datetime.fromtimestamp(
                            result[0][2]) > end or datetime.fromtimestamp(result[0][2]) < datetime.now():
                            con.dispose()
                            return {
                                   'errMsgTitle': 'Attenzione',
                                   'errMsg': 'Prenotazione non consentita.'
                            }, 500
                        #start = datetime.now().date()
                        #end = start + timedelta(days=3)

                        today_reservations = Reservations.query.filter_by(username=username).filter(
                            Reservations.start_time >= start).filter(
                            Reservations.end_time <= end).all()

                        for res in today_reservations:
                            #print(res.start_time, datetime.fromtimestamp(result[0][1]))
                            if res.start_time <= datetime.fromtimestamp(
                                result[0][1]) < res.end_time or \
                                res.start_time < datetime.fromtimestamp(result[0][2]) <= res.end_time:
                                con.dispose()
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

                        #count = Reservations.query.with_for_update().filter_by(
                        #id_lezione=content['id_lezione']).count()
                        count = db.session.query(Reservations.id_corso).filter_by(id_lezione = content['id_lezione']).count()
                        if count > capacity:
                            db.session.rollback()
                            con.dispose()
                            return {
                                   'errMsgTitle': 'Attenzione',
                                   'errMsg': 'Raggiunta la capacità massima consentita.'
                            }, 500

                        else:
                            db.session.commit()
                            con.dispose()

                            return {
                                   "status": "Prenotazione effettuata con successo."
                            }, 200

                    except exc.IntegrityError:
                        db.session.rollback()
                        con.dispose()
                        return {
                           'errMsgTitle': 'Attenzione',
                           'errMsg': 'Prenotazione già effettuata per questa lezione.'
                        }, 500
                    except:
                        db.session.rollback()
                        con.dispose()
                        print("Unexpected error:")
                        print("Title: " + sys.exc_info()[0].__name__)
                        print("Description: " + traceback.format_exc())
                        return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                        }, 500
                else:
                    return {'errMsg': 'Tipo di utente non abilitato alla prenotazione!'}, 500
            else:
                return {'errMsg': 'Wrong username/pass'}, g.status
        else:
            return {'errMsg': 'Payload error!'}, 500

    @ns.doc(security='Basic Auth')
    @token_required_general
    def delete(self, id_prenotazione):
        """Delete Reservation"""
        if g.status == 200:
            username = g.response['user']['userId']
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


class WeekReservationReport(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self,days):
        """Get N days room reservation csv"""

        if g.status == 200:
        
            try:
                userId = username = g.response['user']['userId']
                user = User.query.filter_by(username=userId).join(Role).filter_by(role='admin').first()
                grpId = g.response['user']['grpId']
                if user is not None or grpId == 99:
                    _rooms = Room.query.all()
                    buildings = Area.query.all()
                    _days = []

                    for day in range(0,int(days)):
                        end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        end = end - timedelta(days=day)
                        _start = end - timedelta(days=1)
                        print(_start)
                        print(end)
                        start = _start.timestamp()
                        end = end.timestamp()
                        rooms = []

                        for r in _rooms:
                            if r.id_esse3 != None:
                                rooms.append({
                                    'id': r.id_esse3,
                                    'name':r.room_name,
                                    'build':r.area_id,
                                    'tot': r.capacity,
                                    'ppl': 0
                                    })

                    
                        con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

                        rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND start_time >= '" +str(start) + "' AND end_time <= '" + str(end) + "' AND type != 'W' AND type != 'c' AND type != 'b' AND type != 't' AND type != 'O'")
                    
                        for row in rs:
                            for r in rooms:
                                if int(r['id']) == int(row[35]):
                                    reserv = Reservations.query.filter_by(
                                        id_lezione=row[0]).count()
                                    res = math.floor((reserv + r['ppl'])/2)
                                    r['ppl'] = res
                                    break

                        _days.append({
                            'date': str(_start),
                            'rooms':rooms
                            })

                    return _days
                else:
                   return {"errMsg": "Not Authorized"}, 403
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())

                return {'status': 'error', 'errMsg': traceback.format_exc()}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET ALL GA COURSES -------------

class getAllGACourses(Resource):
    def get(self):
        """Get all GA courses"""
        courses = []

        all_courses = GaTypes.query.all()
        for course in all_courses:
            courses.append({'type': course.type, 'type_name_abb': course.type_name_abb,
                            'type_name_complete': course.type_name_complete})

        return all_courses, 200


# ------------- GET GA LECTURES -------------


class getGALectures(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, type):
        """Get GA Lectures"""
        if g.status == 200:
            username = g.response['user']['userId']

            lectures = []

            _now = datetime.now() + timedelta(hours=6)
            start = _now.replace(hour=18, minute=0, second=0, microsecond=0)
            start = start - timedelta(days=1)

            end = _now.replace(hour=18, minute=0, second=0, microsecond=0)
            end = end + timedelta(days=2)

            start = start.timestamp()
            end = end.timestamp()

            con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

            rs = con.execute(
                "SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND ((start_time >= '" +
                str(datetime.now().timestamp()) + "' AND BINARY type = 'J')  OR (start_time >= '" +
                str(start) + "' AND end_time <= '" + str(end) + "' AND BINARY type == '" + type + "'))"
            )

            for row in rs:
                reserved = False
                resered_id = None
                reserved_by = None
                _reservation = Reservations.query.filter_by(id_lezione=row[0])
                reservation = _reservation.filter_by(username=username)
                res_count = _reservation.count()

                if reservation.first() is not None:
                    reserved = True
                    resered_id = reservation.first().id
                    reserved_by = reservation.first().reserved_by

                capacity = math.floor(int(row[41]) / int(Config.CAPACITY_F))

                lectures.append({
                    'id': row[0],
                    'id_corso': row[32],
                    'start': str(datetime.fromtimestamp(row[1])),
                    'end': str(datetime.fromtimestamp(row[2])),
                    'room': {
                        'name': row[38],
                        'capacity': capacity,
                        'description': row[40],
                        'availability': capacity - res_count
                    },
                    'course_name': row[9],
                    'prof': row[11],
                    'reservation': {
                        'reserved_id': resered_id,
                        'reserved': reserved,
                        'reserved_by': reserved_by
                    }
                })
            con.dispose()

            return lectures, 200
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status