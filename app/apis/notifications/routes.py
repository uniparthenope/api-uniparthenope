from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Notifications', description='Push notifications')

from app.apis.notifications.v1.notifications_v1 import RegisterDevice, UnregisterDevice, GetCdsId, NotificationByCdsId, NotificationByUsername

ns.add_resource(RegisterDevice, '/v1/registerDevice', methods=['POST'])
ns.add_resource(UnregisterDevice, '/v1/unregisterDevice', methods=['POST'])
ns.add_resource(GetCdsId, '/v1/getCdsId', methods=['GET'])
ns.add_resource(NotificationByCdsId, '/v1/notificationByCdsId', methods=['POST'])
ns.add_resource(NotificationByUsername, '/v1/notificationByUsername', methods=['POST'])
