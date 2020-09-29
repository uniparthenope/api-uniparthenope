import base64
import sys
import traceback
from io import BytesIO
import qrcode
from datetime import datetime, timedelta
import random, string
import sqlalchemy

from flask import g, send_file, Response, request
from flask_restplus import Resource, fields

from app.config import Config
from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.apis.badges.models import Badges, Scan
from app.apis.access.models import UserAccess
from app.apis.ga_uniparthenope.models import Reservations
from app.models import User, Role

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- QR-CODE CHECK -------------


insert_token = ns.model("Token", {
    "token": fields.String(description="token", required=True),
    "id_tablet": fields.String(description="identificativo tablet", required=True)
})

def returnMessage(message,duration,color,position):
    return {
        'message': message,
        'duration': int(duration),
        'color': color,
        'position': int(position)
    }


class QrCodeCheck_v2(Resource):
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
                    username = token_string.split(':')[0]
                    grpId = token_string.split(':')[2]

                    badge = Badges.query.filter_by(token=content['token']).first()
                    if badge is not None:
                        if datetime.now() < badge.expire_time:
                            user = UserAccess.query.filter_by(username=username).first()
                            if user is not None:
                                if user.autocertification:
                                    if grpId == '6':
                                        matricola = token_string.split(':')[3]
                                        if user.classroom == "presence":
                                            start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).timestamp()
                                            end = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23, 59).timestamp()
                                            reserv = Reservations.query.filter_by(username=username).filter(Reservations.start_time>=datetime.fromtimestamp(start)).filter(Reservations.end_time<=datetime.fromtimestamp(end))

                                            if reserv.count() > 0:
                                                con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)
                                                string = ""
                                                for r in reserv:
                                                    rs = con.execute("SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND E.id ='" + str(r.id_lezione) + "'")
                                                    result = rs.fetchall()
                                                    string += result[0][38] + " " + str(r.start_time.hour) + ":00 " + str(r.end_time.hour) + ":00 \n"

                                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                     username=username, grpId=grpId, matricola=matricola, result="OK", scan_by=g.response['user']['userId'])
                                                db.session.add(u)
                                                db.session.commit()
                                                return returnMessage("\n\nAUTORIZZATO !\n\n" + string,1,"#00AA00",3), 200
                                            else:
                                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                     username=username, grpId=grpId, matricola=matricola, result="OK", scan_by=g.response['user']['userId'])
                                                db.session.add(u)
                                                db.session.commit()
                                                return returnMessage("\n\nAUTORIZZATO !\n\n",1,"#00AA00",3), 200
                                        else:
                                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                     username=username, grpId=grpId, matricola=matricola, result="Tipo di accesso non in presenza!", scan_by=g.response['user']['userId'])
                                            db.session.add(u)
                                            db.session.commit()
                                            return returnMessage("\n\nNON AUTORIZZATO !\n\nTipo di accesso non in presenza!",1,"#AA0000",3), 500
                                    else:
                                        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                 username=username, grpId=grpId,
                                                 result="OK", scan_by=g.response['user']['userId'])
                                        db.session.add(u)
                                        db.session.commit()
                                        return returnMessage("\n\nAUTORIZZATO !\n\n",1,"#00AA00",3), 200
                                else:
                                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                             username=username, grpId=grpId,
                                             result="Autocertificazione mancante!", scan_by=g.response['user']['userId'])
                                    db.session.add(u)
                                    db.session.commit()
                                    return returnMessage("\n\nNON AUTORIZZATO !\n\nAutocertificazione mancante!",1,"#AA0000",3), 500
                            else:
                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                         username=username, grpId=grpId,
                                         result="Utente non presente nel db.", scan_by=g.response['user']['userId'])
                                db.session.add(u)
                                db.session.commit()
                                return returnMessage("\n\nNON AUTORIZZATO !\n\nUtente non presente nel db. Provare con il proprio username al posto del CF!",1,"#AA0000",3), 500
                        else:
                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                     username=username, grpId=grpId,
                                     result="Token scaduto", scan_by=g.response['user']['userId'])
                            db.session.add(u)
                            db.session.commit()
                            return returnMessage("\n\nNON AUTORIZZATO !\n\nToken scaduto!",1,"#AA0000",3), 500
                    else:
                        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),  result="Token non valido!", scan_by=g.response['user']['userId'])
                        db.session.add(u)
                        db.session.commit()
                        return returnMessage("\n\nNON AUTORIZZATO !\n\nToken non valido!",1,"#AA0000",3), 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())

                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(), result="Qr-code non valido!", scan_by=g.response['user']['userId'])
                    db.session.add(u)
                    db.session.commit()
                    
                    return returnMessage("\n\nNON AUTORIZZATO !\n\nQr-code non valido!",1,"#AA0000",3), 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
