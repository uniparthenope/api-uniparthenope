from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Badges', description='UniParthenope App operations')

from app.apis.badges.v1.badges_v1 import QrCode, QrCodeCheck

ns.add_resource(QrCode, '/v1/generateQrCode', methods=['GET'])
ns.add_resource(QrCodeCheck, '/v1/checkQrCode', methods=['POST'])