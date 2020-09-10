import base64
import sys
import traceback
from datetime import datetime

from babel.numbers import format_currency

from app.apis.uniparthenope.v1.login_v1 import token_required_general
from flask import g, request
from app import api, db
from flask_restplus import Resource, fields, reqparse

from app.models import User
from app.apis.eating.models import UserFood, Food, Ristorante

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
ns = api.namespace('uniparthenope')

# ------------- CREATE USER -------------

user = ns.model("user credentials", {
    "user": fields.String(description="username", required=True),
    "pass": fields.String(description="password", required=True),
    "nome": fields.String(description="nome", required=True),
    "cognome": fields.String(description="cognome", required=True),
    "email": fields.String(description="email", required=True),
    "nome_bar": fields.String(description="nome bar di appartenenza", required=True),
    "grpDes": fields.String(description="gruppo di appartenenza", required=True),
    "grpId": fields.String(description="Id gruppo", required=True),
    "sex": fields.String(description="sesso (M/F)", required=True),
    "tel": fields.String(description="telefono", required=True),
    "img": fields.String(description="immagine", required=True)
})


class newUser(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(user)
    def post(self):
        """New user"""
        content = request.json

        if g.status == 200:
            if 'user' in content and 'pass' in content and 'nome' in content and 'cognome' in content and 'email' in content and 'nome_bar' in content and 'img' in content and 'grpDes' in content and 'grpId' in content and 'tel' in content and 'sex' in content:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                user = User.query.filter_by(username=userId).first()
                if user is not None:
                    for x in user.roles:
                        if x.role == 'admin':
                            try:
                                if content['img'] != "":
                                    image_data = content['img']
                                    image_data = bytes(image_data, encoding="ascii")
                                else:
                                    image_data = None

                                u = UserFood(username=content['user'], nome=content['nome'], cognome=content['cognome'], email=content['email'],
                                             bar=content['nome_bar'], image=image_data, grpId=content['grpId'], grpDes=content['grpDes'], telefono=content['tel'], sesso=content['sex'])
                                u.set_password(content['pass'])
                                db.session.add(u)
                                db.session.commit()
                                return {'message': 'User added'}, 200
                            except:
                                print("Unexpected error:")
                                print("Title: " + sys.exc_info()[0].__name__)
                                print("Description: " + traceback.format_exc())
                                return {
                                           'errMsgTitle': sys.exc_info()[0].__name__,
                                           'errMsg': traceback.format_exc()
                                       }, 500
                else:
                    return {'errMsg': 'No admin'}, 403
            else:
                return {'errMsg': 'Missing username/password'}, 502
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- CREATE RESTAURANT -------------

risto = ns.model("restaurant credentials", {
    "name": fields.String(description="name", required=True),
    "tel": fields.String(description="telephone", required=True),
    "p_iva": fields.String(description="p. IVA", required=True),
    "place": fields.String(description="place", required=True),
    "email": fields.String(description="email", required=True),
    "img": fields.String(description="image", required=True)
})


class newRisto(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(risto)
    def post(self):
        """New restaurant"""
        content = request.json

        if g.status == 200:
            if 'name' in content and 'tel' in content and 'p_iva' in content and 'place' in content and 'email' in content and 'img' in content:
                base64_bytes = g.token.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                token_string = message_bytes.decode('utf-8')
                userId = token_string.split(':')[0]

                user = User.query.filter_by(username=userId).first()
                if user is not None:
                    for x in user.roles:
                        if x.role == 'admin':
                            try:
                                if content['img'] != "":
                                    image_data = content['img']
                                    image_data = bytes(image_data, encoding="ascii")
                                else:
                                    image_data = None

                                u = Ristorante(nome_bar=content['name'], telefono=content['tel'], p_iva=content['p_iva'], email=content['email'],
                                             luogo=content['place'], image=image_data)
                                db.session.add(u)
                                db.session.commit()
                                return {'message': 'Risto added'}, 200
                            except:
                                print("Unexpected error:")
                                print("Title: " + sys.exc_info()[0].__name__)
                                print("Description: " + traceback.format_exc())
                                return {
                                           'errMsgTitle': sys.exc_info()[0].__name__,
                                           'errMsg': traceback.format_exc()
                                       }, 500
                else:
                    return {'errMsg': 'No admin'}, 403
            else:
                return {'errMsg': 'Missing username/password'}, 502
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- GET TODAY ALL MENU -------------

class getAllToday(Resource):
    def get(self):
        """Get today all menu"""
        all_menu = []
        today = datetime.today()

        try:
            ristoranti = Ristorante.query.all()
            for risto in ristoranti:
                array = []
                for food in risto.users:
                    for f in food.foods:
                        if (f.data.year == today.year and f.data.month == today.month and f.data.day == today.day) or f.sempre_attivo:
                            if f.image is None:
                                image = ""
                            else:
                                image = (f.image).decode('ascii')

                            menu = ({'nome': f.nome,
                                 'descrizione': f.descrizione,
                                 'prezzo': format_currency(f.prezzo, 'EUR', locale='it_IT'),
                                 'tipologia': f.tipologia,
                                 'sempre_attivo': f.sempre_attivo,
                                 'pubblicato_da': f.user_username,
                                 'image': image})

                            array.append(menu)

                if risto.image is None:
                    risto_image = ""
                else:
                    risto_image = (risto.image).decode('ascii')

                all_menu.append({
                    "info": {
                        "nome": risto.nome_bar,
                        "email": risto.email,
                        "p_iva": risto.p_iva,
                        "luogo": risto.luogo,
                        "tel": risto.telefono,
                        "image": risto_image
                    },
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


# ------------- GET ALL SPECIFIED USER'S MENU -------------

class getMenuBar(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    def get(self):
        """Get all specified user's menu"""

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
                             'prezzo': format_currency(f.prezzo, 'EUR', locale='it_IT'),
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
