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
from app.apis.access.models import UserAccess
from app.log.log import time_log


url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- CLASSROOM -------------

access = ns.model("access", {
    "accessType": fields.String(description="undefined|presence|distance", required=True)
})


class Access(Resource):
    @time_log(title="ACCESS_V1", filename="access_v1.log", funcName="Access POST")
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(access)
    def post(self):
        """Modify classroom"""

        content = request.json

        if g.status == 200:
            try:
                r = g.response
                userId = ['user']['userId']

                if r['user']['grpId'] == 7 or r['user']['grpId'] == 99 or r['user']['grpId'] == 97 or r['user']['grpId'] == 98:
                    return {'errMsg': 'Operazione non consentita!'}, 403
                else:
                    if 'accessType' in content:
                        if content['accessType'] == 'presence' or content['accessType'] == 'distance' or content[
                            'accessType'] == 'undefined':
                            user = UserAccess.query.filter_by(username=userId).first()

                            if user is None:
                                try:
                                    if content['accessType'] == "presence" and (
                                            user.autocertification == False or user.autocertification is None):
                                        return {'errMsg': 'Permesso negato. Autocertificazione mancante!'}, 500

                                    else:
                                        if r['user']['grpId'] == 6:
                                            u = UserAccess(username=userId,
                                                           classroom=content['accessType'],
                                                           grpId=r['user']['grpId'], persId=r['user']['persId'],
                                                           stuId=r['user']['trattiCarriera'][0]['stuId'],
                                                           matId=r['user']['trattiCarriera'][0]['matId'],
                                                           matricola=r['user']['trattiCarriera'][0]['matricola'],
                                                           cdsId=r['user']['trattiCarriera'][0]['cdsId'])
                                        else:
                                            u = UserAccess(username=userId, classroom=content['accessType'],
                                                           grpId=r['user']['grpId'], persId=None,
                                                           stuId=None, matId=None, matricola="", cdsId=None)
                                        db.session.add(u)
                                        db.session.commit()

                                        return {'message': 'Classroom modified'}, 200

                                except AttributeError:
                                    db.session.rollback()
                                    return {
                                               'errMsgTitle': 'Attenzione',
                                               'errMsg': 'Non è possibile scegliere la modalità "in presenza" senza aver accettato l\'autocertificazione obbligatoria!'
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
                                try:
                                    if content['accessType'] == "presence" and (
                                            user.autocertification == False or user.autocertification is None):
                                        return {'errMsg': 'Permesso negato. Autocertificazione mancante!'}, 500
                                    else:
                                        user.classroom = content['accessType']
                                        db.session.commit()
                                        return {'message': 'Classroom modified'}, 200
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

    @time_log(title="ACCESS_V1", filename="access_v1.log", funcName="Access GET")
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get classroom"""

        if g.status == 200:
            try:

                r = g.response

                userId = r['user']['userId']

                user = UserAccess.query.filter_by(username=userId).first()
                if r['user']['grpId'] == 6:
                    if r['user']['userId'] != userId:
                        user = UserAccess.query.filter_by(username=r['user']['userId']).first()

                if user is not None:
                    if user.persId == "":
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


# ------------- CERTIFICATION -------------

covidStatement = ns.model("covidStatement", {
    "covidStatement": fields.Boolean(description="true|false", required=True)
})


class Certification(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(covidStatement)
    def post(self):
        """Modify covidStatement"""

        content = request.json

        if g.status == 200:
            try:
                r = g.response

                userId = r['user']['userId']

                if 'covidStatement' in content:
                    if content['covidStatement'] == True or content['covidStatement'] == False:
                        user = UserAccess.query.filter_by(username=userId).first()

                        if user is None:
                            try:
                                if r['user']['grpId'] == 6:
                                    u = UserAccess(username=r['user']['userId'], classroom="undefined",
                                                   autocertification=content['covidStatement'],
                                                   grpId=r['user']['grpId'],
                                                   persId=r['user']['persId'],
                                                   stuId=r['user']['trattiCarriera'][0]['stuId'],
                                                   matId=r['user']['trattiCarriera'][0]['matId'],
                                                   matricola=r['user']['trattiCarriera'][0]['matricola'],
                                                   cdsId=r['user']['trattiCarriera'][0]['cdsId'])
                                elif r['user']['grpId'] == 7:
                                    u = UserAccess(username=userId,
                                                   autocertification=content['covidStatement'], classroom="undefined",
                                                   grpId=r['user']['grpId'], persId=r['user']['docenteId'], stuId=None,
                                                   matId=None, matricola="", cdsId=None)
                                else:
                                    u = UserAccess(username=userId, classroom="undefined",
                                                   autocertification=content['covidStatement'], grpId=r['user']['grpId'], persId=None,
                                                   stuId=None, matId=None, matricola="", cdsId=None)
                                db.session.add(u)
                                db.session.commit()

                                return {'message': 'Covid Statement modified'}, 200

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
                                if user.classroom == "presence" and content['covidStatement'] == False:
                                    return {'errMsg': 'Operazione non consetita. Si è scelto di seguire in presenza!'}, 500
                                else:
                                    user.autocertification = content['covidStatement']
                                    db.session.commit()
                                    return {'message': 'Covid Statement modified'}, 200
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
        """Get covidStatement"""

        if g.status == 200:
            try:
                r = g.response

                userId = r['user']['userId']

                user = UserAccess.query.filter_by(username=userId).first()

                if r['user']['grpId'] == 6:
                    if r['user']['userId'] != userId:
                        user = UserAccess.query.filter_by(username=r['user']['userId']).first()

                if user is not None:
                    if user.persId == "":
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
                        return {"covidStatement": user.autocertification}, 200
                    else:
                        return {"covidStatement": user.autocertification}, 200
                else:
                    return {"covidStatement": False}, 200
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

            user = User.query.filter_by(username=userId).join(Role).filter_by(
                role='admin').first() or User.query.filter_by(username=userId).join(Role).filter_by(role='pta').first()
            if user is not None:
                def generate():
                    try:
                        users = UserAccess.query.all()

                        data = StringIO()
                        writer = csv.writer(data)

                        writer.writerow((
                            "username", "grpId", "persId/docenteId", "stuId", "matId", "cdsId", "matricola",
                            "scelta", "dichiarazione"))
                        yield data.getvalue()
                        data.seek(0)
                        data.truncate(0)
                        for row in users:
                            row.username = re.sub(',', '', row.username)
                            row.username = re.sub('|', '', row.username)
                            row.username = re.sub(' ', '', row.username)

                            writer.writerow((row.username, row.grpId, row.persId, row.stuId, row.matId, row.cdsId,
                                             row.matricola, row.classroom, row.autocertification))
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


# ------------- COVID ALERT -------------


class CovidAlert(Resource):
    def get(self):
        """Get codiv alert message"""

        return {
                   "title": "DICHIARAZIONE PER IL CONTENIMENTO DEL COVID-19",
                   "body": '<div>In relazione a quanto previsto dalle Linee guida per il contenimento della diffusione del covid-19 in materia di accesso alle sedi universitarie, confermo</div>' +
                           '<ul>' +
                           '<li>di non essere affetto da COVID-19 o di non essere stato sottoposto a periodo di quarantena obbligatoria di almeno 14 giorni;</li>' +
                           '<li>di non accusare sintomi riconducibili al COVID-19 quali, a titolo esemplificativo, temperatura corporea superiore a 37,5&deg;C, tosse, raffreddore e di non aver avuto contatti con persona affetta da COVID-19 negli ultimi 14 giorni;</li>' +
                           '<li>l&#39;impegno a rinunciare all&rsquo;accesso alle sedi dell&rsquo;Universit&agrave; degli Studi Parthenope e ad informare l&#39;Autorit&agrave; sanitaria competente nell&#39;ipotesi in cui qualsiasi dei predetti sintomi dovesse emergere prima, durante o dopo la frequentazione delle strutture di questo Ateneo;</li>' +
                           '</ul>'
               }, 200
