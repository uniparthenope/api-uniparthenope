import base64
import io
import json
import sys
import traceback
from io import BytesIO
import qrcode
from datetime import datetime, timedelta
import random, string

import requests
import sqlalchemy

from flask import g, send_file, Response, request
from flask_restplus import Resource, fields

from app.apis.uniparthenope.v1.general_v1 import Anagrafica
from app.config import Config
from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.apis.badges.models import Badges, Scan, UserScan, TempScanNotification
from app.apis.access.models import UserAccess
from app.apis.ga_uniparthenope.models import Reservations
from app.log.log import time_log

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


# ------------- QR-CODE -------------


def randomword(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


class QrCode_v2(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.produces(['image/png'])
    def get(self):
        """Get qr-code image"""

        if g.status == 200:
            try:
                if 'Token-notification' in request.headers:
                    if g.response['user']['grpId'] == 6:
                        token_qr = g.response['user']['userId'] + ";" + randomword(30) + ";" + str(
                            g.response['user']['grpId']) + ";" + g.response['user']['trattiCarriera'][0]['matricola']
                    else:
                        token_qr = g.response['user']['userId'] + ";" + randomword(30) + ";" + str(
                            g.response['user']['grpId'])

                    token_qr_notification = token_qr + ";" + request.headers['Token-notification']

                    token_qr_final = (base64.b64encode(bytes(str(token_qr).encode("utf-8")))).decode('utf-8')
                    token_qr_final_notification = (
                        base64.b64encode(bytes(str(token_qr_notification).encode("utf-8")))).decode('utf-8')

                    expire_data = datetime.now() + timedelta(minutes=10)

                    badge = Badges(token=token_qr_final, expire_time=expire_data)
                    db.session.add(badge)
                    db.session.commit()

                    pil_img = qrcode.make(token_qr_final_notification)
                    img_io = BytesIO()
                    pil_img.save(img_io, 'PNG')
                    img_io.seek(0)
                    return send_file(img_io, mimetype='image/png', cache_timeout=-1)
                else:
                    return {'errMsg': 'Payload error!'}, 500
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {'errMsg': 'Image creation error'}, 500

        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- QR-CODE CHECK -------------


insert_token = ns.model("Token", {
    "token": fields.String(description="token", required=True),
    "id_tablet": fields.String(description="identificativo tablet", required=True)
})


def returnMessage(message, duration, color, position):
    return {
        'message': message,
        'duration': int(duration),
        'color': color,
        'position': int(position)
    }


class QrCodeCheck_v2(Resource):
    @time_log(title="BADGES_V2", filename="badges_v2.log", funcName="QrCodeCheck_v2")
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(insert_token)
    def post(self):
        """Check QrCode"""
        content = request.json

        if g.status == 200:
            if 'token' in content and 'id_tablet' in content:
                try:
                    base64_bytes = content['token'].encode('utf-8')
                    message_bytes = base64.b64decode(base64_bytes)
                    token_string = message_bytes.decode('utf-8')
                    username = token_string.split(';')[0]
                    grpId = token_string.split(';')[2]

                    badge = Badges.query.filter_by(token=content['token']).first()
                    if badge is not None:
                        if datetime.now() < badge.expire_time:
                            user = UserAccess.query.filter_by(username=username).first()
                            if user is not None:
                                if user.autocertification:
                                    if grpId == '6':
                                        matricola = token_string.split(';')[3]
                                        if user.classroom == "presence":
                                            start = datetime(datetime.now().year, datetime.now().month,
                                                             datetime.now().day, 0, 0).timestamp()
                                            end = datetime(datetime.now().year, datetime.now().month,
                                                           datetime.now().day, 23, 59).timestamp()
                                            reserv = Reservations.query.filter_by(username=username).filter(
                                                Reservations.start_time >= datetime.fromtimestamp(start)).filter(
                                                Reservations.end_time <= datetime.fromtimestamp(end))

                                            if reserv.count() > 0:
                                                con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                                                string = ""
                                                for r in reserv:
                                                    ##TODO SISTEMARE LA QUERY SULLE RESERVATIONS
                                                    rs = con.execute(
                                                        "SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND E.id ='" + str(
                                                            r.id_lezione) + "'")
                                                    result = rs.fetchall()
                                                    if len(result) != 0:
                                                        string += result[0][38] + " " + str(
                                                            r.start_time.hour) + ":00 " + str(
                                                            r.end_time.hour) + ":00 \n"
                                                    else:
                                                        string += ""

                                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                         username=username, grpId=grpId, matricola=matricola,
                                                         result="OK", scan_by=g.response['user']['userId'])
                                                db.session.add(u)
                                                db.session.commit()
                                                return returnMessage("\n\nAUTORIZZATO !\n\n" + string, 1, "#00AA00",
                                                                     3), 200
                                            else:
                                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                         username=username, grpId=grpId, matricola=matricola,
                                                         result="OK", scan_by=g.response['user']['userId'])
                                                db.session.add(u)
                                                db.session.commit()
                                                return returnMessage("\n\nAUTORIZZATO !\n\n", 1, "#00AA00", 3), 200
                                        else:
                                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                     username=username, grpId=grpId, matricola=matricola,
                                                     result="Tipo di accesso non in presenza!",
                                                     scan_by=g.response['user']['userId'])
                                            db.session.add(u)
                                            db.session.commit()
                                            return returnMessage(
                                                "\n\nNON AUTORIZZATO !\n\nTipo di accesso non in presenza!", 1,
                                                "#AA0000", 3), 500
                                    else:
                                        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                 username=username, grpId=grpId,
                                                 result="OK", scan_by=g.response['user']['userId'])
                                        db.session.add(u)
                                        db.session.commit()
                                        return returnMessage("\n\nAUTORIZZATO !\n\n", 1, "#00AA00", 3), 200
                                else:
                                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                             username=username, grpId=grpId,
                                             result="Autocertificazione mancante!",
                                             scan_by=g.response['user']['userId'])
                                    db.session.add(u)
                                    db.session.commit()
                                    return returnMessage("\n\nNON AUTORIZZATO !\n\nAutocertificazione mancante!", 1,
                                                         "#AA0000", 3), 500
                            else:
                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                         username=username, grpId=grpId,
                                         result="Utente non presente nel db.", scan_by=g.response['user']['userId'])
                                db.session.add(u)
                                db.session.commit()
                                return returnMessage(
                                    "\n\nNON AUTORIZZATO !\n\nUtente non presente nel db. Provare con il proprio username al posto del CF!",
                                    1, "#AA0000", 3), 500
                        else:
                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                     username=username, grpId=grpId,
                                     result="Token scaduto", scan_by=g.response['user']['userId'])
                            db.session.add(u)
                            db.session.commit()
                            return returnMessage("\n\nNON AUTORIZZATO !\n\nToken scaduto!", 1, "#AA0000", 3), 500
                    else:
                        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(), result="Token non valido!",
                                 scan_by=g.response['user']['userId'])
                        db.session.add(u)
                        db.session.commit()
                        return returnMessage("\n\nNON AUTORIZZATO !\n\nToken non valido!", 1, "#AA0000", 3), 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())

                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(), result="Qr-code non valido!",
                             scan_by=g.response['user']['userId'])
                    db.session.add(u)
                    db.session.commit()

                    return returnMessage("\n\nNON AUTORIZZATO !\n\nQr-code non valido!", 1, "#AA0000", 3), 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- SEND REQUEST INFO -------------


insert_token_notification = ns.model("TokenNotification", {
    "myToken": fields.String(description="token", required=True),
    "receivedToken": fields.String(description="token", required=True)
})


class sendRequestInfo(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(insert_token_notification)
    def post(self):
        """Send request Info"""
        content = request.json

        if g.status == 200:
            if 'myToken' in content and 'receivedToken' in content:
                try:
                    base64_bytes = content['receivedToken'].encode('utf-8')
                    message_bytes = base64.b64decode(base64_bytes)
                    token_string = message_bytes.decode('utf-8')

                    grpId = token_string.split(';')[2]

                    if grpId == '6':
                        receivedToken = token_string.split(';')[4]
                    else:
                        receivedToken = token_string.split(';')[3]

                    try:
                        x = UserScan(user_A=g.response['user']['userId'], user_B=token_string.split(';')[0])
                        db.session.add(x)
                        db.session.commit()

                        headers = {
                            'Content-Type': "application/json",
                            "Authorization": "key=" + Config.API_KEY_FIREBASE
                        }

                        # TODO dare titolo a notifica
                        body = {
                            "notification": {
                                "title": 'Richiesta informazioni',
                                "body": g.response['user']['userId'] + " vorrebbe ottenere le tue informazioni.",
                                "badge": "1",
                                "sound": "default",
                                "showWhenInForeground": "true",
                            },
                            "data": {
                                "receivedToken": content['myToken'],
                                "page": "info",
                                "id": x.id
                            },
                            "content_avaible": True,
                            "priority": "High",
                            "to": receivedToken
                        }

                        firebase_response = requests.request("POST", "https://fcm.googleapis.com/fcm/send", json=body,
                                                             headers=headers, timeout=5)

                        if firebase_response.status_code == 200:
                            return {
                                       "status": "success",
                                       "message": "Notifica inviata con successo!"
                                   }, 200
                    except:
                        db.session.rollback()

                except requests.exceptions.HTTPError as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except requests.exceptions.ConnectionError as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except requests.exceptions.Timeout as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except requests.exceptions.RequestException as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())
                    return {
                               "status": "Error",
                               "message": traceback.format_exc()
                           }, 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- SEND INFO -------------


insert_token_notification_info = ns.model("TokenNotificationInfo", {
    "receivedToken": fields.String(description="token", required=True),
    "id": fields.String(description="id_transaction", required=True)
})


class sendInfo(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(insert_token_notification)
    def post(self):
        """Send Info"""
        content = request.json

        if g.status == 200:
            if 'receivedToken' in content and 'id' in content:
                # TODO inserire esito in una tabella
                try:
                    if g.response['user']['grpId'] == 6:
                        id = str(g.response['user']['persId'])
                    elif g.response['user']['grpId'] == 7:
                        id = str(g.response['user']['docenteId'])

                    info = Anagrafica(Resource).get(id)
                    info_json = json.loads(json.dumps(info))[0]

                    if g.response['user']['grpId'] == 6:
                        info_json['matricola'] = g.response['user']['trattiCarriera'][0]['matricola']
                    info_json['username'] = g.response['user']['userId']
                    info_json['ruolo'] = g.response['user']['grpDes']

                    try:
                        record = UserScan.query.filter_by(id=content['id']).first()
                        record.result = "Accepted"

                        x = TempScanNotification(response=info_json, username=record.user_A)
                        db.session.add(x)
                        db.session.commit()

                        headers = {
                            'Content-Type': "application/json",
                            "Authorization": "key=" + Config.API_KEY_FIREBASE
                        }

                        body = {
                            "notification": {
                                "title": 'Informazioni ottenute',
                                "body": g.response['user']['userId'] + " ha condiviso le sue informazioni.",
                                "badge": "1",
                                "sound": "default",
                                "showWhenInForeground": "true",
                            },
                            "data": {
                                "page": "info_received",
                                "id_info": x.id
                            },
                            "content_avaible": True,
                            "priority": "High",
                            "to": content['receivedToken']
                        }

                        firebase_response = requests.request("POST", "https://fcm.googleapis.com/fcm/send", json=body,
                                                             headers=headers, timeout=5)

                        if firebase_response.status_code == 200:
                            return {
                                       "status": "success",
                                       "message": "Notifica inviata con successo!"
                                   }, 200
                    except:
                        db.session.rollback()
                except requests.exceptions.HTTPError as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except requests.exceptions.ConnectionError as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except requests.exceptions.Timeout as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except requests.exceptions.RequestException as e:
                    return {
                               "status": "Error",
                               "message": str(e)
                           }, 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())
                    return {
                               "status": "Error",
                               "message": traceback.format_exc()
                           }, 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
