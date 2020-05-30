import base64
from io import BytesIO
import qrcode
from datetime import datetime, timedelta
import random, string

from flask import g, send_file, Response, request
from flask_restplus import Resource

from app import api
from app.apis.uniparthenope.v1.login_v1 import token_required_general
from app.apis.badges.models import Badges

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def randomword(length):
   letters = string.ascii_lowercase+string.digits
   return ''.join(random.choice(letters) for i in range(length))


# ------------- QR-CODE -------------


class QrCode(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.produces(['image/png'])
    def get(self):
        """Get qr-code image"""

        if g.status == 200:
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                token_qr = userId + ":" + randomword(30)
                print(token_qr)
                token_qr_final = base64.b64encode(bytes(str(token_qr).encode("utf-8")))
                print(token_qr_final)

                expire_data = datetime.now() + timedelta(minutes=1)
                print(expire_data)

                pil_img = qrcode.make(token_qr_final)
                img_io = BytesIO()
                pil_img.save(img_io, 'PNG')
                img_io.seek(0)
                return send_file(img_io, mimetype='image/png', cache_timeout=-1)
            except:
                return {'errMsg': 'Image creation error'}, 500

        else:
            return {'errMsg': 'Wring username/pass'}, g.status