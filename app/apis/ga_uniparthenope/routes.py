from app import api

version = "1.0"
ver = "v1"

ns = api.namespace('GAUniparthenope', description='Calendar')

from app.apis.ga_uniparthenope.v1.ga_v1 import SearchCourse, OtherCourses, ProfessorCourse, getTodayLecture, getLectures, getStudentsList, setReservation

ns.add_resource(SearchCourse, '/v1/searchCourse/<nome_area>/<nome_corso>/<nome_prof>/<nome_studio>/<periodo>', methods=['GET'])
ns.add_resource(OtherCourses, '/v1/otherCourses/<periodo>', methods=['GET'])
ns.add_resource(ProfessorCourse, '/v1/professorCourse/<periodo>/<cognome>', methods=['GET'])
ns.add_resource(getTodayLecture, '/v1/getTodayLecture/<id_corso>', methods=['GET'])
ns.add_resource(getLectures, '/v1/getLectures/<id_corso>', methods=['GET'])
ns.add_resource(getStudentsList, '/v1/getStudentsList/<id_lezione>', methods=['GET'])
ns.add_resource(setReservation, '/v1/setPrenotazione', methods=['POST'])
