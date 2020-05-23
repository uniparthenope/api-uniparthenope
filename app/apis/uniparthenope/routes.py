from app import api

version = "1.0"
ver = "v1"
url = "https://uniparthenope.esse3.cineca.it/e3rest/api/"

ns = api.namespace('UniparthenopeApp', description='UniParthenope App operations')

from app.apis.uniparthenope.v1.login_v1 import Login, Logout
from app.apis.uniparthenope.v1.students_v1 import GetPianoId, GetAverage, GetTotalExams, GetExams, CheckExam, CheckAppello, CheckPrenotazione, getReservations, ExamsToFreq, getProfessors
from app.apis.uniparthenope.v1.professor_v1 import getCourses, getSession
from app.apis.uniparthenope.v1.general_v1 import CurrentAA, RecentAD, InfoCourse, InfoPersone

ns.add_resource(Login, '/v1/login', methods=['GET'])
ns.add_resource(Logout, '/v1/logout', methods=['GET'])


ns.add_resource(GetPianoId, '/v1/students/pianoId/<stuId>', methods=['GET'])
ns.add_resource(GetAverage, '/v1/students/average/<matId>/<value>', methods=['GET'])
ns.add_resource(GetTotalExams, '/v1/students/totalExams/<matId>', methods=['GET'])
ns.add_resource(GetExams, '/v1/students/exams/<stuId>/<pianoId>', methods=['GET'])
ns.add_resource(CheckExam, '/v1/students/checkExams/<matId>/<adsceId>', methods=['GET'])
ns.add_resource(CheckAppello, '/v1/students/checkAppello/<cdsId>/<adId>', methods=['GET'])
ns.add_resource(CheckPrenotazione, '/v1/students/checkPrenotazione/<cdsId>/<adId>/<appId>/<stuId>', methods=['GET'])
ns.add_resource(getReservations, '/v1/students/getReservations/<matId>', methods=['GET'])
ns.add_resource(ExamsToFreq, '/v1/students/examsToFreq/<stuId>/<pianoId>/<matId>', methods=['GET'])
ns.add_resource(getProfessors, '/v1/students/getProfessors/<aaId>/<cdsId>', methods=['GET'])


ns.add_resource(getCourses, '/v1/professor/getCourses/<aaId>', methods=['GET'])
ns.add_resource(getSession, '/v1/professor/getSession', methods=['GET'])


ns.add_resource(CurrentAA, '/v1/general/current_aa/<cdsId>', methods=['GET'])
ns.add_resource(RecentAD, '/v1/general/recentAD/<adId>', methods=['GET'])
ns.add_resource(InfoCourse, '/v1/general/infoCourse/<adLogId>', methods=['GET'])
ns.add_resource(InfoPersone, '/v1/general/persone/<nome_completo>', methods=['GET'])