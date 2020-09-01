import base64
import sys
import traceback
import csv
from io import StringIO
import re

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general

from flask import g, request
from flask_restplus import Resource, fields
from werkzeug import Response

from app.models import User, Role
from app.apis.access.models2 import UserAccessFull

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

                r = g.response

                if 'accessType' in content:
                    print(content['accessType'])
                    if content['accessType'] == 'presence' or content['accessType'] == 'distance' or content['accessType'] == 'undefined':
                        user = UserAccessFull.query.filter_by(username=userId).first()
                        if user is None:
                            try:
                                if r['user']['grpId'] == 6:
                                    u = UserAccessFull(username=r['user']['userId'], classroom=content['accessType'], grpId=r['user']['grpId'], persId=r['user']['persId'], stuId=r['user']['trattiCarriera'][0]['stuId'], matId=r['user']['trattiCarriera'][0]['matId'],matricola=r['user']['trattiCarriera'][0]['matricola'],cdsId=r['user']['trattiCarriera'][0]['cdsId'])
                                elif r['user']['grpId'] == 7:
                                    u = UserAccessFull(username=userId, classroom=content['accessType'], grpId=r['user']['grpId'], persId=r['user']['docenteId'], stuId="", matId="",matricola="",cdsId="")
                                else:
                                    u = UserAccessFull(username=userId, classroom=content['accessType'],
                                                       grpId="", persId="",
                                                       stuId="", matId="", matricola="", cdsId="")
                                db.session.add(u)
                                db.session.commit()

                                return {'message': 'Classroom modified'}, 200

                            except:
                                print("Unexpected error:")
                                print("Title: " + sys.exc_info()[0].__name__)
                                print("Description: " + traceback.format_exc())
                                return {
                                           'errMsgTitle': sys.exc_info()[0].__name__,
                                           'errMsg': traceback.format_exc()
                                       }, 500
                        else:
                            try:
                                user.classroom = content['accessType']
                                db.session.commit()
                                return {'message': 'Classroom modified'}, 200
                            except:
                                print("Unexpected error:")
                                print("Title: " + sys.exc_info()[0].__name__)
                                print("Description: " + traceback.format_exc())
                                return {
                                           'errMsgTitle': sys.exc_info()[0].__name__,
                                           'errMsg': traceback.format_exc()
                                       }, 500
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

                r = g.response

                user = UserAccessFull.query.filter_by(username=userId).first()
                if user is not None:
                    if user.persId is "":
                        if r['user']['grpId'] == 6:
                            user.grpId = r['user']['grpId']
                            user.persId = r['user']['persId']
                            user.stuId = r['user']['trattiCarriera'][0]['stuId']
                            user.matId = r['user']['trattiCarriera'][0]['matId']
                            user.matricola = r['user']['trattiCarriera'][0]['matricola']
                            user.cdsId = r['user']['trattiCarriera'][0]['cdsId']
                            db.session.commit()
                        elif r['user']['grpId'] == 7:
                            user.grpId = r['user']['grpId']
                            user.persId = r['user']['persId']
                            db.session.commit()
                        return {"accessType": user.classroom}, 200
                    else:
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


# ------------- CSV -------------


class getCompleteCSV(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.produces(['text/csv'])
    def get(self):
        """Get CSV access"""
        if g.status == 200:
            base64_bytes = g.token.encode('utf-8')
            message_bytes = base64.b64decode(base64_bytes)
            token_string = message_bytes.decode('utf-8')
            userId = token_string.split(':')[0]

            user = User.query.filter_by(username=userId).join(Role).filter_by(role='admin').first() or User.query.filter_by(username=userId).join(Role).filter_by(role='pta').first()
            if user is not None:
                def generate():
                    try:
                        users = UserAccessFull.query.all()

                        data = StringIO()
                        writer = csv.writer(data)

                        writer.writerow(("username", "grpId", "persId/docenteId", "stuId", "matId", "matricola", "scelta"))
                        yield data.getvalue()
                        data.seek(0)
                        data.truncate(0)
                        for row in users:
                            row.username = re.sub(',', '', row.username)
                            row.username = re.sub('|', '', row.username)
                            row.username = re.sub(' ', '', row.username)

                            writer.writerow((row.username, row.grpId, row.persId, row.stuId, row.matId, row.matricola, row.classroom))
                            yield data.getvalue()
                            data.seek(0)
                            data.truncate(0)
                    except:
                        print("Unexpected error:")
                        print("Title: " + sys.exc_info()[0].__name__)
                        print("Description: " + traceback.format_exc())
                        return {
                                   'errMsgTitle': sys.exc_info()[0].__name__,
                                   'errMsg': traceback.format_exc()
                               }, 500

                response = Response(generate(), mimetype='text/csv')
                response.headers.set("Content-Disposition", "attachment", filename="access.csv")
                return response
            else:
                return {'errMsg': 'Not Authorized!'}, 403
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status