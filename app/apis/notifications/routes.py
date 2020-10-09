from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Notifications', description='Push notifications')

from app.apis.notifications.v1.notifications_v1 import RegisterDevice

ns.add_resource(RegisterDevice, '/v1/registerDevice', methods=['POST'])
