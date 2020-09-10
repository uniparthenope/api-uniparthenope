from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Access', description='UniParthenope access operations')

from app.apis.access.v1.access_v1 import Access, getCompleteCSV, CovidAlert, Certification

ns.add_resource(Access, '/v1/classroom', methods=['GET', 'POST'])
ns.add_resource(Certification, '/v1/covidStatement', methods=['GET', 'POST'])
ns.add_resource(getCompleteCSV, '/v1/getCSV', methods=['GET'])
ns.add_resource(CovidAlert, '/v1/covidAlert', methods=['GET'])
