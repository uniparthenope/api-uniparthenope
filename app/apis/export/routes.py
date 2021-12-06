from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Reports', description='UniParthenope csv reports for PTA/Admin')

from app.apis.export.v1.export_v1 import ReportsCSV

ns.add_resource(ReportsCSV, '/v1/getCSV', methods=['POST'])
