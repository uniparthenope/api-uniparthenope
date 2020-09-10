from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Access', description='UniParthenope access operations')

from app.apis.access.v1.access_v1 import Access, getCompleteCSV

ns.add_resource(Access, '/v1/classroom', methods=['GET', 'POST'])
ns.add_resource(getCompleteCSV, '/v1/general/CSV', methods=['GET'])

