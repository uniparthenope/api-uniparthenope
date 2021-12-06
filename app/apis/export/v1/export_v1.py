import sys
import traceback
import csv
from io import StringIO

from app import api, db
from app.apis.uniparthenope.v1.login_v1 import token_required_general, token_required

from flask import g, request
from flask_restplus import Resource, fields
from werkzeug import Response

import sqlalchemy
from sqlalchemy import exc

from app.models import User, Role
from app.apis.badges.models import Scan
from app.config import Config

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')


def create_csv(rs, building):
    def generate():
        try:
            data = StringIO()
            w = csv.writer(data)

            w.writerow(("datetime", "total"))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

            for row in rs:
                w.writerow((row[0].strftime("%Y-%m-%d"), row[1]))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
        except:
            return {
                'errMsgTitle': sys.exc_info()[0].__name__,
                'errMsg': traceback.format_exc()
            }, 50

    response = Response(generate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename= building + ".csv")
    return response


report = ns.model("report_data", {
    "start_time": fields.String(description="YYYY-MM-DD 00:00:00", required=True),
    "end_time": fields.String(description="YYYY-MM-DD 00:00:00", required=True),
    "building": fields.String(description="CDN or PACA or ...", required=True)
})

class ReportsCSV(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(report)
    @ns.produces(['text/csv'])
    def post(self):
        """Return CSV report daily access"""
        content = request.json

        if 'start_time' in content and 'end_time' in content and 'building' in content:
            if g.status == 200:
                admin = User.query.filter_by(username=g.response['user']['userId']).join(Role, Role.user_id == User.id).filter(
                    Role.role == 'admin').first()


                if admin is not None:
                    try:
                        con = sqlalchemy.create_engine(Config.SQLALCHEMY_BINDS['badges'], echo=False)

                        rs = con.execute("select time_stamp, count(*) from scan where id_tablet LIKE '%%" + content['building'] + "%%' AND result = 'OK' AND time_stamp >= '" + content['start_time'] + "' and time_stamp < '" + content['end_time'] + "' group by DATE_FORMAT(time_stamp, '%%c %%d %%Y')")

                        return create_csv(rs, content['building'])

                        con.dispose()
                    except:
                        print("Unexpected error:")
                        print("Title: " + sys.exc_info()[0].__name__)
                        print("Description: " + traceback.format_exc())
                        return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                        }, 500
                else:
                    return {'errMsg': 'User not authorized!'}, 401
            else:
                return {'errMsg': 'Errore username/pass!'}, g.status
        else:
            return {'errMsg': 'Payload error!'}, 500
