import base64
import sys
import traceback
from io import BytesIO
import qrcode
from datetime import datetime, timedelta
import random, string

from flask import g, send_file, Response, request
from flask_restplus import Resource, fields
from sqlalchemy import desc

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.apis.badges.models import Badges, Scan, Tablets
from app.apis.access.models import UserAccess
from app.models import User, Role
from app.log.log import time_log

from app.config import Config


url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def randomword(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


# ------------- QR-CODE -------------


class QrCode(Resource):
    @time_log(title="BADGES_V1", filename="badges_v2.log", funcName="GetQrCode")
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.produces(['image/png'])
    def get(self):
        """Get qr-code image"""

        if g.status == 200 or g.status == 202:
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                if g.response['user']['grpId'] == 6:
                    token_qr = userId + ":" + randomword(30) + ":" + str(g.response['user']['grpId']) + ":" + g.response['user']['trattiCarriera'][0]['matricola']
                else:
                    token_qr = userId + ":" + randomword(30) + ":" + str(g.response['user']['grpId'])

                #print(token_qr)
                token_qr_final = (base64.b64encode(bytes(str(token_qr).encode("utf-8")))).decode('utf-8')
                #print(token_qr_final)

                expire_data = datetime.now() + timedelta(minutes=10)
                #print(expire_data)

                badge = Badges(token=token_qr_final, expire_time=expire_data)
                db.session.add(badge)
                db.session.commit()

                pil_img = qrcode.make(token_qr_final)
                img_io = BytesIO()
                pil_img.save(img_io, 'PNG')
                img_io.seek(0)
                return send_file(img_io, mimetype='image/png', cache_timeout=-1)
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


class QrCodeCheck(Resource):
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
                                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                     username=username, grpId=grpId, matricola=matricola, result="OK", scan_by=g.response['user']['userId'])
                                            db.session.add(u)
                                            db.session.commit()
                                            return {'status': 'Ok'}, 200
                                        else:
                                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                     username=username, grpId=grpId, matricola=matricola, result="Tipo di accesso non in presenza!", scan_by=g.response['user']['userId'])
                                            db.session.add(u)
                                            db.session.commit()
                                            return {'status': 'error', 'errMsg': 'Tipo di accesso non in presenza!'}, 500
                                    else:
                                        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                                 username=username, grpId=grpId,
                                                 result="OK", scan_by=g.response['user']['userId'])
                                        db.session.add(u)
                                        db.session.commit()
                                        return {'status': 'Ok'}, 200
                                else:
                                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                             username=username, grpId=grpId,
                                             result="Autocertificazione mancante!", scan_by=g.response['user']['userId'])
                                    db.session.add(u)
                                    db.session.commit()
                                    return {'status': 'error', 'errMsg': 'Autocertificazione mancante!'}, 500
                            else:
                                u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                         username=username, grpId=grpId,
                                         result="Autocertificazione mancante!", scan_by=g.response['user']['userId'])
                                db.session.add(u)
                                db.session.commit()
                                return {'status': 'error', 'errMsg': 'Autocertificazione mancante!'}, 500
                        else:
                            u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),
                                     username=username, grpId=grpId,
                                     result="Token scaduto", scan_by=g.response['user']['userId'])
                            db.session.add(u)
                            db.session.commit()
                            return {'status': 'error', 'errMsg': 'Token scaduto!'}, 500
                    else:
                        u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(),  result="Token non valido!", scan_by=g.response['user']['userId'])
                        db.session.add(u)
                        db.session.commit()
                        return {'status': 'error', 'errMsg': 'Token non valido!'}, 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())

                    u = Scan(id_tablet=content['id_tablet'], time_stamp=datetime.now(), result="Qr-code non valido!", scan_by=g.response['user']['userId'])
                    db.session.add(u)
                    db.session.commit()

                    return {'status': 'error', 'errMsg': 'Qr-code non valido!'}, 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- QR-CODE STATUS -------------

parser = api.parser()
parser.add_argument('tabletId', type=str, help='Id tablet')

@ns.doc(parser=parser)
class QrCodeStatus(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    
    def get(self, tabletId):
        """Get qr-code status by interval"""
        
        if g.status == 200:
            
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]
                grpId = g.response['user']['grpId']

                user = User.query.filter_by(username=userId).join(Role).filter_by(role='admin').first() or User.query.filter_by(username=userId).join(Role).filter_by(role='pta').first()
                if user is not None or grpId == 99:
                    if tabletId is None or tabletId == "--":
                        tabletId = ""
                    #print(datetime.now()-timedelta(minutes=3600), datetime.now())

                    total_gp = UserAccess.query.filter(UserAccess.greenpass == True).count()
                    
                    # DAY UPDATES
                    time_now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

                    ok_count = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result == "OK").filter(Scan.id_tablet.like("%" + tabletId + "%")).count()

                    ok_verified = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%COVID-19 verificata%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()


                    bad_gp_notver = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%non verificata!%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    bad_gp_miss = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%Mancante!%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    bad_gp_fake = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%non corrisponde%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    bad_gp_expired = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%COVID-19 Scaduta%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()

                    bad_token_count = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%Token%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    bad_qr_count = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result.like("%Qr-code%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()

                    # LIVE UPDATES
                    #time_now = datetime.now()
                    #interval = int(interval)
                    #ok_count = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result == "OK").filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    
                    #ok_verified = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%COVID-19 verificata%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()


                    #bad_gp_notver = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%non verificata!%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    #bad_gp_miss = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%Mancante!%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    #bad_gp_fake = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%non corrisponde%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    #bad_gp_expired = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%COVID-19 Scaduta%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    
                    #bad_token_count = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%Token%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
                    #bad_qr_count = Scan.query.filter(Scan.time_stamp.between(time_now - timedelta(seconds=interval),time_now)).filter(Scan.result.like("%Qr-code%")).filter(Scan.id_tablet.like("%" + tabletId + "%")).count()
            
                    ok_general = ok_count + ok_verified

                    bad_gp = bad_gp_notver + bad_gp_miss + bad_gp_fake + bad_gp_expired
                    bad_count = bad_token_count + bad_qr_count + bad_gp
            
                    total_count = ok_general + bad_count
                    fail = {
                        "total": bad_count,
                        "total_gp": bad_gp,
                        "gp_notver": bad_gp_notver,
                        "gp_miss":bad_gp_miss,
                        "gp_fake":bad_gp_fake,
                        "gp_expired": bad_gp_expired,

                        "expired_token": bad_token_count,
                        "unknown_user": bad_qr_count,
                        }
                    success ={
                            "total": ok_general,
                            "ok_count": ok_count,
                            "ok_gp": ok_verified
                            }
                    return [{
                        "timeStamp": str((datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")),
                        "total": total_count,
                        "total_gp": total_gp,
                        "success": success,
                        "fail" : fail
                        }], 200
            
                else:
                    return {'errMsg': 'Not Authorized!'}, 403   
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())

                return {'status': 'error', 'errMsg': traceback.format_exc()}, 500


buildings = ['PAC','CDN','NOLA','ACTON','MED','VDDA']

def queryBuilding(building):

    time_now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    ok_count = Scan.query.filter(Scan.time_stamp > time_now).filter(Scan.result == "OK").filter(
        Scan.id_tablet.like("%" + building + "%")).count()

    ok_verified = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%COVID-19 verificata%")).filter(
        Scan.id_tablet.like("%" + building + "%")).count()

    bad_gp_notver = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%non verificata!%")).filter(Scan.id_tablet.like("%" + building + "%")).count()
    bad_gp_miss = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%Mancante!%")).filter(Scan.id_tablet.like("%" + building + "%")).count()
    bad_gp_fake = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%non corrisponde%")).filter(Scan.id_tablet.like("%" + building + "%")).count()
    bad_gp_expired = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%COVID-19 Scaduta%")).filter(
        Scan.id_tablet.like("%" + building + "%")).count()

    bad_token_count = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%Token%")).filter(Scan.id_tablet.like("%" + building + "%")).count()
    bad_qr_count = Scan.query.filter(Scan.time_stamp > time_now).filter(
        Scan.result.like("%Qr-code%")).filter(Scan.id_tablet.like("%" + building + "%")).count()

    ok_general = ok_count + ok_verified

    bad_gp = bad_gp_notver + bad_gp_miss + bad_gp_fake + bad_gp_expired
    bad_count = bad_token_count + bad_qr_count + bad_gp

    total_count = ok_general + bad_count
    fail = {
        "total": bad_count,
        "total_gp": bad_gp,
        "gp_notver": bad_gp_notver,
        "gp_miss": bad_gp_miss,
        "gp_fake": bad_gp_fake,
        "gp_expired": bad_gp_expired,

        "expired_token": bad_token_count,
        "unknown_user": bad_qr_count,
    }
    success = {
        "total": ok_general,
        "ok_count": ok_count,
        "ok_gp": ok_verified
    }
    return [{
        'name': building,
        "total": total_count,
        "success": success,
        "fail": fail
    }]

class QrCodeStatusAll(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get all buildings qr-code status"""

        if g.status == 200:

            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]
                grpId = g.response['user']['grpId']

                user = User.query.filter_by(username=userId).join(Role).filter_by(
                    role='admin').first() or User.query.filter_by(username=userId).join(Role).filter_by(
                    role='pta').first()
                if user is not None or grpId == 99:
                    total_gp = UserAccess.query.filter(UserAccess.greenpass == True).count()
                    _buildings = []
                    for b in buildings:
                        _buildings.append(queryBuilding(b))

                    return{
                        "timeStamp": str((datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")),
                        'total_gp' : total_gp,
                        'buildings': _buildings
                          }, 200

                else:
                    return {'errMsg': 'Not Authorized!'}, 403
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())

                return {'status': 'error', 'errMsg': traceback.format_exc()}, 500

inf_token = ns.model("Machine", {
    "machine_id": fields.String(description="Machine ID", required=True),
    "position": fields.String(description="Machine Position", required=True),
    "version": fields.String(description="Machine Version", required=True),
})


class SyncMachine(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(inf_token)
    def post(self):
        """Synchronize Scanner"""

        content = request.json

        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')
        userId = token_string.split(':')[0]

        if g.status == 200:
            admin = User.query.filter_by(username=userId).join(Role, Role.user_id == User.id).filter(
                Role.role == 'admin').first()

            if 'machine_id' in content and 'position' in content and 'version' in content:

                if content['position'] in Config.SEDI_UNP:

                    try:
                        if g.response['user']['grpId'] == 99 or admin is not None:

                            machine = Tablets.query.filter_by(machine_id=content['machine_id']).first()
                            pos = Tablets.query.filter(Tablets.position.like('%' + content['position'] + '%'))
                            current_name = content['position'] + '-' + str(pos.count()+1)
                            arr = ","
                            for y in pos:
                                name = y.current_name.split("-")[1] + ","
                                arr = arr + name

                            for x in range(1,len(arr)):
                                search_x = "," + str(x) + ","
                                if search_x not in arr:
                                    current_name = content['position'] + '-' + str(x)
                                    break

                            if machine is not None:
                                if machine.position != content['position']:

                                    machine.current_name = current_name
                                    machine.position = content['position']
                                    machine.version = content['version']

                                    db.session.commit()

                                    return {'current_name': current_name}, 200
                                else:

                                    return {'errMsg': 'Position has not changed!'}, 500
                            else:

                                x = Tablets(machine_id=content['machine_id'], default_name='CHANGE',
                                              current_name=current_name, position=content['position'], version=str(content['version']))
                                db.session.add(x)
                                db.session.commit()

                                return {'current_name': current_name}, 200

                        else:
                            return {'errMsg': 'User not authorized!'}, 401

                    except:
                        print("Unexpected error:")
                        print("Title: " + sys.exc_info()[0].__name__)
                        print("Description: " + traceback.format_exc())
                        return {'errMsg': 'Sync Tablet Error'}, 500
                else:
                    return {'errMsg': 'Sede non corretta!'}, 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status

class ScanHistory(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general

    def get(self):
        """Get university access history"""

        base64_bytes = g.token.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        token_string = message_bytes.decode('utf-8')
        userId = token_string.split(':')[0]

        if g.status == 200:
            scans = Scan.query.filter_by(username=userId).order_by(desc('time_stamp')).all()

            if len(scans) > 0:
                history = []
                for scan in scans:
                    history.append({
                        'timestamp': str(scan.time_stamp),
                        'tablet': scan.id_tablet,
                        'result': scan.result
                    })
                return history

            else:
                return {'errMsg': 'Nessuno scan disponibile'}, 500

        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
