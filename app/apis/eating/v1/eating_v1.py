import base64
from datetime import datetime

from app.apis.uniparthenope.v1.login_v1 import token_required_general
from flask import g, request
from app import api
from flask_restplus import Resource, fields

from app.models import User
from app.apis.eating.models import UserFood, Food

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- INSERT USER -------------

user = ns.model("user credentials",
                {
                    "user": fields.String(description="username", required=True),
                    "pass": fields.String(description="password", required=True)
                }
                )


class newUser(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(user)
    def post(self):
        """New user"""
        content = request.json

        if g.status == 200:
            if 'user' in content and 'pass' in content:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                user = User.query.filter_by(username=userId).first()
                if user is not None:
                    for x in user.roles:
                        if x.role == 'admin':
                            print("admin")

                else:
                    return {'errMsg': 'No admin'}, 403
            else:
                return {'errMsg': 'Missing username/password'}, 502
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET USERS NAME BAR -------------

class getUsers(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        if g.status == 200:
            array = []

            users = UserFood.query.all()
            for f in users:
                array.append(f.nome_bar)
            return array, 200
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET TODAY MENU -------------

class getToday(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):

        if g.status == 200:
            array = []
            today = datetime.today()

            foods = Food.query.all()

            for f in foods:
                if (f.data.year == today.year \
                    and f.data.month == today.month \
                    and f.data.day == today.day) \
                        or f.sempre_attivo:
                    if f.image is None:
                        image = ""
                    else:
                        image = (f.image).decode('ascii')

                    menu = ({'nome': f.nome,
                             'descrizione': f.descrizione,
                             'prezzo': f.prezzo,
                             'tipologia': f.tipologia,
                             'sempre_attivo': f.sempre_attivo,
                             'nome_bar': f.user_username,
                             'image': image})
                    array.append(menu)

            return array, 200
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status