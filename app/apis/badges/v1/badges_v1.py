import base64
import sys
import traceback
from io import BytesIO
import qrcode
from datetime import datetime, timedelta
import random, string

from flask import g, send_file, Response, request
from flask_restplus import Resource, fields

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.apis.badges.models import Badges
from app.apis.access.models import UserAccess

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def randomword(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


# ------------- QR-CODE -------------


class QrCode(Resource):
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

                token_qr = userId + ":" + randomword(30) + ":" + str(g.response['user']['grpId'])
                print(token_qr)
                token_qr_final = (base64.b64encode(bytes(str(token_qr).encode("utf-8")))).decode('utf-8')
                print(token_qr_final)

                expire_data = datetime.now() + timedelta(minutes=10)
                print(expire_data)

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


insert_token = ns.model("Token", {"token": fields.String(description="token", required=True)})


class QrCodeCheck(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(insert_token)
    def post(self):
        """Check QrCode"""
        content = request.json

        if g.status == 200:
            if 'token' in content:
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
                                print(user.autocertification)
                                if user.autocertification:
                                    if grpId == 6:
                                        if user.classroom == "presence":
                                            return {'status': 'Ok'}, 200
                                        else:
                                            return {'status': 'error', 'errMsg': 'Tipo di accesso non in presenza!'}, 500
                                    else:
                                        return {'status': 'Ok'}, 200
                                else:
                                    return {'status': 'error', 'errMsg': 'Autocertificazione mancante!'}, 500
                            else:
                                return {'status': 'error', 'errMsg': 'Autocertificazione mancante!'}, 500
                        else:
                            return {'status': 'error', 'errMsg': 'Token scaduto!'}, 500
                    else:
                        return {'status': 'error', 'errMsg': 'Token non valido!'}, 500
                except:
                    print("Unexpected error:")
                    print("Title: " + sys.exc_info()[0].__name__)
                    print("Description: " + traceback.format_exc())
                    return {
                               'errMsgTitle': sys.exc_info()[0].__name__,
                               'errMsg': traceback.format_exc()
                           }, 500
            else:
                return {'errMsg': 'Error payload'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
