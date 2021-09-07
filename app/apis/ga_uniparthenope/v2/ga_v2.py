import sys
import traceback

import sqlalchemy
from datetime import datetime, timedelta
import math

from sqlalchemy import exc

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.config import Config

from app.apis.ga_uniparthenope.models import Reservations, Area

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

            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=2)
            start = start.timestamp()
            end = end.timestamp()

            con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

            rs = con.execute(
                "SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND start_time >= '" +
                str(start) + "' AND end_time <= '" + str(end) + "' AND type != 'W' AND type != 'c' AND type != 'b' AND type != 't' AND type != 'O'")

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

                areas[row[37] - 1]['services'].append({
                    'id': row[0],
                    'id_corso': row[32],
                    'start': str(datetime.fromtimestamp(row[1])),
                    'end': str(datetime.fromtimestamp(row[2])),
                    'room': {
                        'name': row[38],
                        'capacity': math.floor(int(row[41]) / 2),
                        'description': row[40],
                        'availability': math.floor(int(row[41]) / 2) - Reservations.query.with_for_update().filter_by(
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
            return areas, 200
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- CLASSROOMS RESERVATIONS -------------


prenotazione_aule = ns.model("services_reservation", {
    "id_entry": fields.String(description="", required=True),
    "matricola": fields.String(description="", required=True)
})


class RoomsReservation(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(prenotazione_aule)
    def post(self):
        """Set Rooms Reservation"""
        content = request.json

        if 'id_lezione' in content and 'matricola' in content:
            if g.status == 200:
                try:
                    username = g.response['user']['userId']

                    con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                    rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.id = '" + content[
                        'id_lezione'] + "' AND E.room_id = R.id")

                    result = rs.fetchall()
                    capacity = int(result[0][41]) / 2

                    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    end = start + timedelta(days=2)

                    if datetime.fromtimestamp(result[0][1]) < start or datetime.fromtimestamp(
                            result[0][2]) > end or datetime.fromtimestamp(result[0][2]) < datetime.now():
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
                        if res.start_time <= datetime.fromtimestamp(
                                result[0][1]) < res.end_time or \
                                res.start_time < datetime.fromtimestamp(result[0][2]) <= res.end_time:
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

