from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Badges', description='UniParthenope App operations')

from app.apis.badges.v1.badges_v1 import QrCode, QrCodeCheck, QrCodeStatus
from app.apis.badges.v2.badges_v2 import QrCodeCheck_v2

ns.add_resource(QrCode, '/v1/generateQrCode', methods=['GET'])
ns.add_resource(QrCodeCheck, '/v1/checkQrCode', methods=['POST'])
ns.add_resource(QrCodeCheck_v2, '/v2/checkQrCode', methods=['POST'])
ns.add_resource(QrCodeStatus, '/v1/QrCodeStatus/<int:interval>/<tabletId>', methods=['GET'])
