from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Badges', description='UniParthenope App operations')

from app.apis.badges.v1.badges_v1 import QrCode, QrCodeCheck, QrCodeStatus, SyncMachine, ScanHistory
from app.apis.badges.v2.badges_v2 import QrCode_v2, QrCodeCheck_v2, QrCode_v2_SPID, sendRequestInfo, sendInfo, getContactInfo
from app.apis.badges.v3.badges_v3 import QrCodeCheck_v3, GreenPassCheck

ns.add_resource(QrCode, '/v1/generateQrCode', methods=['GET'])
ns.add_resource(QrCodeCheck, '/v1/checkQrCode', methods=['POST'])
ns.add_resource(QrCodeStatus, '/v1/QrCodeStatus/<int:interval>/<tabletId>', methods=['GET'])
ns.add_resource(SyncMachine, '/v1/SyncMachine', methods=['POST'])
ns.add_resource(ScanHistory, '/v1/ScanHistory', methods=['GET'])


ns.add_resource(QrCode_v2, '/v2/generateQrCode', methods=['GET'])
ns.add_resource(QrCode_v2_SPID, '/v2/generateQrCodeSPID', methods=['POST'])
ns.add_resource(QrCodeCheck_v2, '/v2/checkQrCode', methods=['POST'])
ns.add_resource(sendRequestInfo, '/v2/sendRequestInfo', methods=['POST'])
ns.add_resource(sendInfo, '/v2/sendInfo', methods=['POST'])
ns.add_resource(getContactInfo, '/v2/getContactInfo', methods=['POST'])


ns.add_resource(QrCodeCheck_v3, '/v3/checkQrCode', methods=['POST'])
ns.add_resource(GreenPassCheck, '/v3/checkGreenPass', methods=['POST'])
