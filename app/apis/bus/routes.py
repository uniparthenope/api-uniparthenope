from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('Bus', description='UniParthenope App operations')

from app.apis.bus.v1.anm_v1 import ANMSchedule, ANMBus

ns.add_resource(ANMSchedule, '/v1/orari/<sede>', methods=['GET'])
ns.add_resource(ANMBus, '/v1/bus/<sede>', methods=['GET'])