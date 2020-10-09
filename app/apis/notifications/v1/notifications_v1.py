import sys
import traceback
from app import api, db

from flask import g, request
from flask_restplus import Resource, fields
from werkzeug import Response
from sqlalchemy import exc

from app.apis.uniparthenope.v1.login_v1 import token_required_general

from app.log.log import time_log
from app.models import UserNotifications, Devices

ns = api.namespace('uniparthenope')

# ------------- REGISTER USER'S DEVICE -------------

info = ns.model("devices_info", {
    "token": fields.String(description="Token devices", required=True),
    "device_model": fields.String(description="Token devices", required=True),
    "os_version": fields.String(description="Token devices", required=True)
})

class RegisterDevice(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(info)

    def post(self):
        """Register device"""

        content = request.json

        if g.status == 200:
            if 'token' in content and 'device_model' in content and 'os_version' in content:
                try:
                    userId = g.response['user']['userId']
                    user = UserNotifications.query.filter_by(username=userId).first()
                    db.session.flush()
                    if user is not None:
                        user.devices.append(Devices(token=content['token'],device_model=content['device_model'],os_version=content['os_version']))
                        db.session.commit()
                    else:
                        user = UserNotifications(username=userId)
                        user.devices.append(Devices(token=content['token'],device_model=content['device_model'],os_version=content['os_version']))
                        db.session.add(user)
                        db.session.commit()

                    return {
                        "status": "OK"
                    }, 200

                except exc.IntegrityError:
                    db.session.rollback()
                    return{
                        'errMsgTitle': "Attenzione",
                        'errMsg': "Device già registrato"
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
                return {'errMsg': 'Wrong body!'}, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


