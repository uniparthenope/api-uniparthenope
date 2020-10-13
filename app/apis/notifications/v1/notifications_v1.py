import json
import sys
import traceback
import requests

from app import api, db, Config

from flask import g, request
from flask_restplus import Resource, fields
from sqlalchemy import exc

from app.apis.uniparthenope.v1.login_v1 import token_required_general

from app.models import UserNotifications, Devices, User, Role

url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"
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
                        user.devices.append(Devices(token=content['token'], device_model=content['device_model'],
                                                    os_version=content['os_version']))
                        db.session.commit()
                    else:
                        user = UserNotifications(username=userId)
                        user.devices.append(Devices(token=content['token'], device_model=content['device_model'],
                                                    os_version=content['os_version']))
                        db.session.add(user)
                        db.session.commit()

                    return {
                               "status": "OK"
                           }, 200

                except exc.IntegrityError:
                    db.session.rollback()
                    return {
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


# ------------- GET ALL CDSID -------------


class GetCdsId(Resource):
    def get(self):
        """Get all cdsId"""
        array = []

        try:
            response = requests.request("GET", url + "offerta-service-v1/offerte?aaOffId=2020", timeout=5)
            _response = response.json()

            if response.status_code == 200:
                for i in range(len(_response)):
                    array.append({
                        'cdsDes': _response[i]['cdsDes'],
                        'cdsCod': _response[i]['cdsCod'],
                        'cdsOffId': _response[i]['cdsOffId']
                    })
                return array, 200
            else:
                return {'errMsg': _response['retErrMsg']}, response.status_code

        except requests.exceptions.HTTPError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.ConnectionError as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.Timeout as e:
            return {'errMsg': str(e)}, 500
        except requests.exceptions.RequestException as e:
            return {'errMsg': str(e)}, 500
        except:
            return {'errMsg': 'generic error'}, 500


# ------------- SEND NOTIFICATION BY CDSID -------------


notification_cdsId = ns.model("notification_cdsId", {
    "cdsId": fields.String(description="codice corso di studio", required=True),
    "title": fields.String(description="titolo della notifica", required=True),
    "body": fields.String(description="messaggio della notifica", required=True)
})


class NotificationByCdsId(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(notification_cdsId)
    def post(self):
        """Send notification by cdsId"""

        content = request.json

        if g.status == 200:
            admin = User.query.filter_by(username=g.response['user']['userId']).join(Role, Role.user_id == User.id).filter(
                Role.role == 'admin').first()
            if admin is not None:
                courses_cod = []
                result = GetCdsId.get(self)
                courses = json.loads(json.dumps(result))[0]
                for i in range(len(courses)):
                    courses_cod.append(str(courses[i]['cdsOffId']))

                if 'cdsId' in content and 'title' in content and 'body' in content:
                    if content['cdsId'] in courses_cod:
                        try:
                            headers = {
                                'Content-Type': "application/json",
                                "Authorization": "key=" + Config.API_KEY_FIREBASE
                            }

                            body = {
                                "notification": {
                                    "title": content['title'],
                                    "body": content['body'],
                                    "badge": "1",
                                    "sound": "default",
                                    "showWhenInForeground": "true",
                                },
                                "content_avaible": True,
                                "priority": "High",
                                "to": "/topics/CDS_" + content['cdsId']
                            }

                            firebase_response = requests.request("POST", "https://fcm.googleapis.com/fcm/send", json=body, headers=headers, timeout=5)
                            if firebase_response.status_code == 200:
                                return {"status": "OK"}, 200
                            else:
                                return {"errMsg": firebase_response.content}, firebase_response.status_code

                        except requests.exceptions.HTTPError as e:
                            return {'errMsg': str(e)}, 500
                        except requests.exceptions.ConnectionError as e:
                            return {'errMsg': str(e)}, 500
                        except requests.exceptions.Timeout as e:
                            return {'errMsg': str(e)}, 500
                        except requests.exceptions.RequestException as e:
                            return {'errMsg': str(e)}, 500
                        except:
                            print("Unexpected error:")
                            print("Title: " + sys.exc_info()[0].__name__)
                            print("Description: " + traceback.format_exc())
                            return {
                                       'errMsgTitle': sys.exc_info()[0].__name__,
                                       'errMsg': traceback.format_exc()
                                   }, 500
                    else:
                        return {'errMsg': 'Corso di studi non valido!'}, 500
                else:
                    return {'errMsg': 'Wrong body!'}, 500
            else:
                return {'errMsg': 'User not authorized!'}, 401
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status


# ------------- SEND NOTIFICATION BY USERNAME -------------


notification_username = ns.model("notification_username", {
    "username": fields.String(description="username separati dalla virgola", required=True)
})


class NotificationByUsername(Resource):
    @ns.doc(security='Basic Auth')
    @token_required_general
    @ns.expect(notification_username)
    def post(self):
        """Send notification by username"""

        content = request.json

        if g.status == 200:
            admin = User.query.filter_by(username=g.response['user']['userId']).join(Role, Role.user_id == User.id).filter(
                Role.role == 'admin').first()
            if admin is not None:
                if 'username' in content:
                    user = UserNotifications.query.filter_by(username=content['username']).first()

                    if user is not None:
                        print(user.devices)
                        '''
                        try:
                            headers = {
                                'Content-Type': "application/json",
                                "Authorization": "key=" + Config.API_KEY_FIREBASE
                            }

                            body = {
                                "notification": {
                                    "title": content['title'],
                                    "body": content['body'],
                                    "badge": "1",
                                    "sound": "default",
                                    "showWhenInForeground": "true",
                                },
                                "content_avaible": True,
                                "priority": "High",
                                "to": "/topics/CDS_" + content['cdsId']
                            }

                            firebase_response = requests.request("POST", "https://fcm.googleapis.com/fcm/send", json=body, headers=headers, timeout=5)
                            if firebase_response.status_code == 200:
                                return {"status": "OK"}, 200
                            else:
                                return {"errMsg": firebase_response.content}, firebase_response.status_code

                        except requests.exceptions.HTTPError as e:
                            return {'errMsg': str(e)}, 500
                        except requests.exceptions.ConnectionError as e:
                            return {'errMsg': str(e)}, 500
                        except requests.exceptions.Timeout as e:
                            return {'errMsg': str(e)}, 500
                        except requests.exceptions.RequestException as e:
                            return {'errMsg': str(e)}, 500
                        except:
                            print("Unexpected error:")
                            print("Title: " + sys.exc_info()[0].__name__)
                            print("Description: " + traceback.format_exc())
                            return {
                                       'errMsgTitle': sys.exc_info()[0].__name__,
                                       'errMsg': traceback.format_exc()
                                   }, 500
                        '''
                    else:
                        return {'errMsg': "L'username non ha dispositivi registrati!"}, 500
                else:
                    return {'errMsg': 'Wrong body!'}, 500
            else:
                return {'errMsg': 'User not authorized!'}, 401
        else:
            return {'errMsg': 'Wrong username/pass'}, g.status