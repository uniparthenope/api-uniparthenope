import base64
import sys
import traceback
from datetime import datetime

from app.apis.uniparthenope.v1.login_v1 import token_required_general
from flask import g, request
from app import api, db
from flask_restplus import Resource, fields, reqparse

from app.models import User
from app.apis.eating.models import UserFood, Food

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- INSERT USER -------------

user = ns.model("user credentials", {
    "user": fields.String(description="username", required=True),
    "pass": fields.String(description="password", required=True),
    "email": fields.String(description="password", required=True),
    "nome_bar": fields.String(description="password", required=True)
})


class newUser(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(user)
    def post(self):
        """New user"""
        content = request.json

        if g.status == 200:
            if 'user' in content and 'pass' in content and 'email' in content and 'nome_bar' in content:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                user = User.query.filter_by(username=userId).first()
                if user is not None:
                    for x in user.roles:
                        if x.role == 'admin':
                            try:
                                u = UserFood(username=content['user'], email=content['email'],
                                             nome_bar=content['nome_bar'])
                                u.set_password(content['pass'])
                                db.session.add(u)
                                db.session.commit()
                                return {'message': 'User added'}, 200
                            except:
                                return {'errMsg': 'User already exists!'}, 500
                else:
                    return {'errMsg': 'No admin'}, 403
            else:
                return {'errMsg': 'Missing username/password'}, 502
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET USERS NAME BAR -------------

class getUsers(Resource):
    def get(self):
        array = []

        try:
            users = UserFood.query.all()
            for f in users:
                array.append(f.nome_bar)
            return array, 200
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


# ------------- GET TODAY MENU -------------

class getToday(Resource):
    def get(self):
        """Get Menu Today"""
        try:
            all_menu = []
            today = datetime.today()

            users = UserFood.query.all()
            for u in users:
                foods = UserFood.query.filter_by(username=u.username).first().foods

                array = []
                for f in foods:
                    if (f.data.year == today.year and f.data.month == today.month and f.data.day == today.day) or f.sempre_attivo:
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

                all_menu.append({
                    "bar": u.nome_bar,
                    "menu": array
                })

            return all_menu, 200
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


# ------------- ADD NEW MENU -------------

# file_upload = reqparse.RequestParser()
menu = ns.model("menu", {
    "nome": fields.String(description="nome menu", required=True),
    "descrizione": fields.String(description="descrizione menu", required=True),
    "tipologia": fields.String(description="tipologia (Primo, Secondo...)", required=True),
    "prezzo": fields.Integer(description="prezzo", required=True),
    "attivo": fields.Boolean(description="se il menu resta più giorni attivo", required=True),
    "img": fields.String(description="image", required=True)
})


# file_upload.add_argument('file', type=FileStorage, location='files', required=False, help='file')

class addMenu(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(menu)
    def post(self):
        """Add new menu"""
        '''
        content = request.data.decode()
        print(content)
        '''

        content = request.json

        if g.status == 202:
            try:
                if 'nome' in content and 'descrizione' in content and 'tipologia' in content and 'prezzo' in content and 'attivo' in content and 'img' in content:
                    if content['nome'] == "" or content['descrizione'] == "" or content['tipologia'] == "" or content['prezzo'] == "" or content['attivo'] == "":
                        return {'errMsg': 'Insert all fields'}, 500
                    else:
                        base64_bytes = g.token.encode('utf-8')
                        message_bytes = base64.b64decode(base64_bytes)
                        token_string = message_bytes.decode('utf-8')
                        userId = token_string.split(':')[0]

                        u = UserFood.query.filter_by(username=userId).first()

                        if content['img'] != "":
                            image_data = content['img']
                            image_data = bytes(image_data, encoding="ascii")
                        else:
                            image_data = None

                        u.foods.append(
                            Food(nome=content['nome'], descrizione=content['descrizione'], tipologia=content['tipologia'],
                                 prezzo=content['prezzo'], sempre_attivo=content['attivo'], image=image_data))
                        db.session.add(u)
                        db.session.commit()

                        return {'message': 'Added new menu'}, 200
                else:
                    return {'errMsg': 'Missing values'}, 500
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Unauthorized'}, 403


# ------------- get all specified user's menu -------------

class getMenuBar(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """GET ALL SPECIFIED USER'S MENU"""

        array = []

        if g.status == 202:
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                foods = UserFood.query.filter_by(username=userId).first().foods

                for f in foods:
                    d = f.data.strftime('%Y-%m-%d %H:%M')

                    if f.image is None:
                        image = ""
                    else:
                        image = (f.image).decode('ascii')

                    menu = ({'data': d,
                             'nome': f.nome,
                             'descrizione': f.descrizione,
                             'tipologia': f.tipologia,
                             'prezzo': f.prezzo,
                             'sempre_attivo': f.sempre_attivo,
                             'id': f.id,
                             'image': image
                             })
                    array.append(menu)

                return array, 200
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Unauthorized'}, 403


# ------------- REMOVE MENU BY ID -------------

parser = api.parser()
parser.add_argument('id', type=str, required=True, help='Menu Id')


@ns.doc(parser=parser)
class removeMenu(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self, id):
        """Remove menu by Id"""

        if g.status == 202:
            try:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                food = Food.query.filter_by(id=id).join(UserFood).filter_by(username=userId).first()

                if food is not None:
                    try:
                        db.session.delete(food)
                        db.session.commit()

                        return {'message': 'Removed menu'}, 200
                    except:
                        return {'errMsg': 'Error deleting menu'}, 500
                else:
                    return {'errMsg': 'No Menu with this ID'}, 500
            except:
                print("Unexpected error:")
                print("Title: " + sys.exc_info()[0].__name__)
                print("Description: " + traceback.format_exc())
                return {
                           'errMsgTitle': sys.exc_info()[0].__name__,
                           'errMsg': traceback.format_exc()
                       }, 500
        else:
            return {'errMsg': 'Unauthorized'}, 403
