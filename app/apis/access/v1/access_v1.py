import base64
import sys
import traceback

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general

from flask import g, request
from flask_restplus import Resource, fields

from app.apis.access.models import UserAccess

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- CLASSROOM -------------

access = ns.model("access", {
    "accessType": fields.String(description="undefined|presence|distance", required=True)
})


class Access(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(access)
    def post(self):
        """Modify classroom"""

        content = request.json

        if g.status == 200:
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                if 'accessType' in content:
                    print(content['accessType'])
                    if content['accessType'] == 'presence' or content['accessType'] == 'distance' or content['accessType'] == 'undefined':
                        user = UserAccess.query.filter_by(username=userId).first()
                        if user is None:
                            try:
                                u = UserAccess(username=userId, classroom=content['accessType'])
                                db.session.add(u)
                                db.session.commit()

                                return {'message': 'Classroom modified'}, 200

                            except:
                                return {'errMsg': 'Generic error!'}, 500
                        else:
                            try:
                                user.classroom = content['accessType']
                                db.session.commit()
                                return {'message': 'Classroom modified'}, 200
                            except:
                                return {'errMsg': 'Generic error!'}, 500
                    else:
                        return {'errMsg': 'Wrong body!'}, 500
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status

    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get classroom"""

        if g.status == 200:
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                user = UserAccess.query.filter_by(username=userId).first()
                if user is not None:
                    return {"accessType": user.classroom}, 200
                else:
                    return {"accessType": "undefined"}, 200
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
