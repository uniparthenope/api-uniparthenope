import base64
import sys
import traceback
from datetime import datetime, timedelta
import requests
from codicefiscale import codicefiscale
from app.libs import greenpass

from flask import g, request
from flask_restplus import Resource, fields

from app.config import Config
from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.apis.badges.models import Badges, Scan
from app.apis.access.models import UserAccess
from app.log.log import time_log

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def returnMessage(message, duration, color, position, data='', id=None):
    return {
        'message': message,
        'data': data,
        'id': id,
        'duration': int(duration),
        'color': color,
        'position': int(position)
    }


def check(username, content, msg):
    try:
        headers = {
            'Content-Type': "application/json",
            "Authorization": "Basic " + Config.USER_ROOT
        }

        info_request = requests.request("GET",
                                        url + "anagrafica-service-v2/utenti/" + username,
                                        headers=headers, timeout=5)
        _info = info_request.json()
        _info = _info[0]

        if info_request.status_code == 200:
            x = codicefiscale.decode(_info['codFis'])
            date = x['birthdate']
            info = username + ":" + _info['nome'] + ":" + _info[
                'cognome'] + ":" + date.strftime("%Y-%m-%d")
            message_bytes = info.encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            base64_message = base64_bytes.decode('ascii')

            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                     username=username,
                     result=msg,
                     scan_by=g.response['user']['userId'])
            db.session.add(u)
            db.session.commit()
            return returnMessage("\n\nNON AUTORIZZATO !\n\n" + msg, 1,
                                 "#0703FC", 3, base64_message, u.id), 501
    except:
        message_bytes = username.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                 username=username,
                 result=msg,
                 scan_by=g.response['user']['userId'])
        db.session.add(u)
        db.session.commit()
        print("Description: " + traceback.format_exc())
        return returnMessage("\n\nNON AUTORIZZATO !\n\n" + msg, 1,
                             "#0703FC", 3, base64_message, u.id), 502


# ------------- QR-CODE CHECK -------------

insert_token = ns.model("Token", {
    "token": fields.String(description="token", required=True),
    "id_tablet": fields.String(description="identificativo tablet", required=True)
})


class QrCodeCheck_v3(Resource):
    @time_log(title="BADGES_V3", filename="badges_v3.log", funcName="QrCodeCheck_v3")
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(insert_token)
    def post(self):
        """ Check QrCode """
        content = request.json

        if g.status == 200:
            if 'token' in content and 'id_tablet' in content:
                try:
                    base64_bytes = content['token'].encode('utf-8')
                    message_bytes = base64.b64decode(base64_bytes)
                    token_string = message_bytes.decode('utf-8')
                    username = token_string.split(':')[0]

                    badge = Badges.query.filter_by(token=content['token']).first()
                    if badge is not None:
                        if datetime.now() < badge.expire_time:
                            user = UserAccess.query.filter_by(username=username).first()
                            if user is not None:
                                if user.autocertification and user.GP_expire > datetime.now():
                                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                             username=username, result="OK",
                                             scan_by=g.response['user']['userId'])
                                    db.session.add(u)
                                    db.session.commit()
                                    return returnMessage("\n\nAUTORIZZATO !\n\n", 1, "#00AA00",
                                                         3), 200
                                else:
                                    if datetime.now() < user.GP_expire:
                                        msg = "GreenPass Scaduto!"
                                        user = UserAccess.query.filter_by(username=username).first()
                                        user.autocertification = False
                                        # user.GP_expire = None
                                        db.session.commit()
                                    else:
                                        msg = "GreenPass Mancante!"

                                    return check(username, content, msg)
                            else:
                                u = UserAccess(username=username, persId=None,
                                               stuId=None, matId=None, matricola=None, cdsId=None,
                                               GP_expire="2001-01-01 00:00:00")
                                db.session.add(u)
                                db.session.commit()

                                return check(username, content, "GreenPass Mancante!")
                        else:
                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                     username=username,
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


# ------------- GREENPASS CHECK -------------

insert_token = ns.model("Token_GP", {
    "token_GP": fields.String(description="token greenpass", required=True),
    "data": fields.String(description="data to identify user", required=True),
    "id": fields.String(description="id table scan", required=True)
})


def checkGP(name, surname, birthdate, greenpassToken):
    certificate, is_valid = greenpass.certinfo(greenpassToken.encode('UTF-8'))
    expiry = datetime.strptime(certificate['certificate']['v'][0]['dt'], "%Y-%m-%d") + timedelta(days=270)
    if is_valid and datetime.now() < expiry:
        nameData = certificate['certificate']['nam']['gn']
        surnameData = certificate['certificate']['nam']['fn']
        birthdateData = certificate['certificate']['dob']

        if nameData == name and surnameData == surname and birthdate == birthdateData:
            return True, expiry, "GreenPass valido!"
        else:
            return False, expiry, "ATTENZIONE! \nL'utente non corrisponde!"
    else:
        return False, expiry, "GreenPass non valido!"


class GreenPassCheck(Resource):
    @time_log(title="BADGES_V3", filename="badges_v3.log", funcName="GreenPassCheck")
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(insert_token)
    def post(self):
        """ GreenPass QrCode """
        content = request.json
        print(content)

        if g.status == 200:
            if 'token_GP' in content and 'data' in content and 'id' in content:
                try:
                    base64_bytes = content['data'].encode('utf-8')
                    message_bytes = base64.b64decode(base64_bytes)
                    token_string = message_bytes.decode('utf-8')

                    username = token_string.split(':')[0]
                    name_data = token_string.split(':')[1]
                    surname_data = token_string.split(':')[2]
                    birthdate_data = token_string.split(':')[3]

                    result, expiry, msg = checkGP(name_data, surname_data, birthdate_data, content['token_GP'])

                    if content['id'] is not None:
                        record = Scan.query.filter_by(id=content['id']).first()
                        if record is not None:
                            record.result = msg
                            db.session.commit()

                    if result:
                        user = UserAccess.query.filter_by(username=username).first()
                        user.autocertification = True
                        user.GP_expire = expiry
                        db.session.commit()

                        return returnMessage("\n\nAUTORIZZATO !\n\n" + msg, 1, "#00AA00", 3), 200
                    else:
                        return returnMessage("\n\nNON AUTORIZZATO !\n\n" + msg, 1, "#AA0000", 3), 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())

                    return returnMessage("\n\nNON AUTORIZZATO !\n\nToken non valido!", 1, "#AA0000", 3), 500
            else:
                print("QUI")
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
