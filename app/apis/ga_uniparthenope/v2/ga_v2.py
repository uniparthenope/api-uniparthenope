import sqlalchemy
from datetime import datetime

from app import api
from app.apis.uniparthenope.v1.login_v1 import token_required
from app.config import Config

from flask_restplus import Resource
from flask import g

ns = api.namespace('uniparthenope')


# ------------- GET ALL TODAY ROOMS -------------


class getAllTodayRooms(Resource):
    @ns.doc(security='Basic Auth')
    @token_required
    def get(self):
        """Get ALl Today Rooms"""
        if g.status == 200:
            con = sqlalchemy.create_engine(Config.GA_DATABASE, echo=False)

            start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).timestamp()
            end = datetime(datetime.now().year, datetime.now().month, datetime.now().day + 1, 23, 59).timestamp()

            rs = con.execute(
                "SELECT * FROM `mrbs_entry` E JOIN `mrbs_room` R WHERE E.room_id = R.id AND start_time >= '" +
                str(start) + "' AND end_time <= '" + str(end) + "'")

            for row in rs:
                print(row)
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status
