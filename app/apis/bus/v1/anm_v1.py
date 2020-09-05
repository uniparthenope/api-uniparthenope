import sys
import traceback

from app import api
from bs4 import BeautifulSoup
from flask_restplus import Resource
import urllib.request, urllib.error, urllib.parse
from app.apis.bus.bus import glob
import requests

ns = api.namespace('uniparthenope')

# ------------- BUS SCHEDULE -------------

parser = api.parser()
parser.add_argument('sede', type=str, required=True, help='')


@ns.doc(parser=parser)
class ANMSchedule(Resource):
    def get(self, sede):
        """Bus Schedule"""

        url_anm = "http://www.anm.it/infoclick/infoclick.php"
        array = []

        try:
            page = urllib.request.urlopen(url_anm)
            soup = BeautifulSoup(page, 'html.parser')
            key = str(soup.find('script'))
            start = key.find("'") + 1
            end = key.find("'", start)
            key_final = key[start:end]

            for i in range(0, len(glob)):
                if glob[i]['nome'] == sede:
                    for j in range(0, len(glob[i]["info"])):
                        array2 = []
                        for k in range(0, len(glob[i]["info"][j])):
                            # print("PALINA = " + glob[i]["info"][j]["linea"][k]["palina"])
                            data = {
                                'Palina': glob[i]["info"][j]["linea"][k]["palina"],
                                'key': key_final
                            }

                            r = requests.post("http://srv.anm.it/ServiceInfoAnmLinee.asmx/CaricaPrevisioni", json=data)
                            response = r.json()
                            # print(response)

                            array_orari = []
                            for x in range(0, len(response["d"])):
                                # print(response["d"][x]["id"])
                                if response["d"][x]["id"] is not None:
                                    item = ({
                                        'time': response["d"][x]["time"],
                                        'tempoRim': response["d"][x]["timeMin"]
                                    })
                                    array_orari.append(item)

                            data_info = {
                                'linea': glob[i]["info"][j]["linea"][k]["bus"],
                                'key': key_final
                            }

                            r_info = requests.post("http://srv.anm.it/ServiceInfoAnmLinee.asmx/CaricaPercorsoLinea",json=data_info)
                            response_info = r_info.json()
                            # print(response)
                            partenza = {}
                            arrivo = {}
                            for f in range(len(response_info["d"])):
                                if response_info["d"][f]["id"] == glob[i]["info"][j]["linea"][k]["palina"]:
                                    partenza = ({
                                        'id': glob[i]["info"][j]["linea"][k]["palina"],
                                        'nome': response_info["d"][f]["nome"],
                                        'lat': response_info["d"][f]["lat"],
                                        'long': response_info["d"][f]["lon"],
                                        'orari': array_orari
                                    })
                                if response_info["d"][f]["id"] == glob[i]["info"][j]["linea"][k]["palina_arrivo"]:
                                    arrivo = ({
                                        'id': glob[i]["info"][j]["linea"][k]["palina_arrivo"],
                                        'nome': response_info["d"][f]["nome"],
                                        'lat': response_info["d"][f]["lat"],
                                        'long': response_info["d"][f]["lon"]
                                    })
                            item = ({'linea': glob[i]["info"][j]["linea"][k]["bus"],
                                     'partenza': partenza,
                                     'arrivo': arrivo})
                            array2.append(item)

                        item = ({'name': glob[i]["info"][j]["nome"],
                                 'linea': array2})
                        array.append(item)
                    return array

                else:
                    return {'errMsg': 'Impossibile recuperare informazioni Orari Bus'}, 500
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500


# ------------- ANM BUS -------------

parser = api.parser()
parser.add_argument('sede', type=str, required=True, help='')


@ns.doc(parser=parser)
class ANMBus(Resource):
    def get(self,sede):
        """Anm Bus"""

        url_anm = "http://www.anm.it/infoclick/infoclick.php"
        array = []

        try:
            page = urllib.request.urlopen(url_anm)
            soup = BeautifulSoup(page, 'html.parser')
            key = str(soup.find('script'))
            start = key.find("'") + 1
            end = key.find("'", start)
            key_final = key[start:end]

            for i in range(0, len(glob)):
                if glob[i]['nome'] == sede:
                    for j in range(0, len(glob[i]["info"])):
                        array2 = []
                        for k in range(0, len(glob[i]["info"][j])):
                            data = {
                                "linea": glob[i]["info"][j]["linea"][k]["bus"],
                                "key": key_final
                            }

                            r = requests.post("http://srv.anm.it/ServiceInfoAnmLinee.asmx/CaricaPosizioneVeicolo", json=data)
                            if r.status_code == 200:
                                response = r.json()

                                if response["d"][0]["stato"] is None:
                                    pos_bus = []
                                    for x in range(0, len(response["d"])):
                                        print(response["d"][x]["linea"])
                                        item = ({
                                            'lat': response["d"][x]["lat"],
                                            'long': response["d"][x]["lon"]
                                        })
                                        pos_bus.append(item)

                                    item = ({'linea': glob[i]["info"][j]["linea"][k]["bus"],
                                             'bus': pos_bus})
                                    array2.append(item)
                                else:
                                    item = ({'linea': glob[i]["info"][j]["linea"][k]["bus"],
                                             'bus': ""})
                                    array2.append(item)

                                item = ({'name': glob[i]["info"][j]["nome"],
                                         'linea': array2})
                                array.append(item)
                            else:
                                return {'errMsg': 'Impossibile recuperare informazioni Bus'}, 500
                    return array

                else:
                    return {'errMsg': 'Impossibile recuperare informazioni Bus'}, 500
        except:
            print("Unexpected error:")
            print("Title: " + sys.exc_info()[0].__name__)
            print("Description: " + traceback.format_exc())
            return {
                       'errMsgTitle': sys.exc_info()[0].__name__,
                       'errMsg': traceback.format_exc()
                   }, 500