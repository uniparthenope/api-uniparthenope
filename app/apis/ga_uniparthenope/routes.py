from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('GAUniparthenope', description='Calendar')

from app.apis.ga_uniparthenope.v1.ga_v1 import SearchCourse, OtherCourses

ns.add_resource(SearchCourse, '/v1/searchCourse/<nome_area>/<nome_corso>/<nome_prof>/<nome_studio>/<periodo>', methods=['GET'])
ns.add_resource(OtherCourses, '/v1/otherCourses/<periodo>', methods=['GET'])