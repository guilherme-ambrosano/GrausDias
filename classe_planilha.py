import importlib
import requests
import json
import pandas as pd
import numpy as np
import datetime
import calendar
from geopy.geocoders import Nominatim

class semLocal(Exception):
    pass

class semConexao(Exception):
    pass

class semCultura(Exception):
    pass

class semJuvenilidade(Exception):
    pass

class semData(Exception):
    pass

class semDados(Exception):
    pass

class semCalculo(Exception):
    pass

class planilha:
    def __init__(self):
        self.frutiferas = pd.read_csv("frutiferas.csv")
        self.local = None
        self.data = None
        self.dias = None
        self.juvenilidade = None
        self.historico = None
        self.NDA = None
        self.dados = None
        self.geolocator = Nominatim(user_agent = "anonymous")
        self.data_final = None
        self.NDA_final = None
        self.acentos = {"à": "a",
                        "á": "a",
                        "â": "a",
                        "ã": "a",
                        "é": "e",
                        "ê": "e",
                        "í": "i",
                        "ó": "o",
                        "ô": "o",
                        "õ": "o",
                        "ú": "u"}
        pass

    def update_frutiferas(self):
        self.frutiferas = pd.read_csv("frutiferas.csv")

    def tirar_acentos(self, x):
        for a in self.acentos:
            x = x.lower().strip().replace(" ", "_").replace(a, self.acentos[a])
        return x

    def set_local(self, local_str = None, lat_str = None, lon_str = None):
        if local_str is not None and (lat_str is not None or lon_str is not None):
            raise semLocal
        elif local_str is None and lat_str is None and lon_str is None:
            raise semLocal
        try:
            if local_str is not None:
                self.local = self.geolocator.geocode(local_str)
            elif lat_str is not None and lon_str is not None:
                try:
                    lat = int(lat_str)
                    lon = int(lon_str)
                except TypeError:
                    raise semLocal
                if lat < -90 or lat > 90 or lon < -180 or lon > 180:
                    raise semLocal
                self.local = self.geolocator.reverse("{0}, {1}".format(lat_str, lon_str))
        except Exception:
            raise semConexao

    def set_cultura(self, cultura_str = None):
        if cultura_str is None or cultura_str == "":
            raise semCultura
        self.update_frutiferas()
        if self.tirar_acentos(cultura_str) in list(map(self.tirar_acentos, self.frutiferas["nome"].tolist())):
            lista_frutiferas = list(map(self.tirar_acentos, self.frutiferas["nome"].tolist()))
            cultura_str = self.tirar_acentos(cultura_str)
            ind = None
            for i in range(len(lista_frutiferas)):
                if lista_frutiferas[i] == cultura_str:
                    ind = i
                    break
            if ind is None:
                raise semCultura
            if not isinstance(ind, int):
                raise semCultura
            self.cultura = self.frutiferas.iloc[[ind]]
        else:
            raise semCultura

    def nova_cultura(self, cultura_str = None, tbase = None, graus_dias = None, chuva = None, tempo = None):
        try:
            float(tbase)
            float(graus_dias)
            float(chuva)
            int(tempo)
        except:
            raise semCultura
        self.update_frutiferas()
        if self.tirar_acentos(cultura_str) in map(self.tirar_acentos, self.frutiferas["nome"].tolist()):
            raise semCultura
        with open("frutiferas.csv", "a") as file:
            file.write("{0},{1},{2},{3},{4}\n".format(str(cultura_str).capitalize(), str(tbase), str(graus_dias), str(chuva), str(tempo)))
        self.update_frutiferas()

    def set_juvenilidade(self, juvenilidade = None):
        if juvenilidade is None:
            raise semJuvenilidade
        try:
            self.juvenilidade = int(juvenilidade)
            if self.juvenilidade < 0 or self.juvenilidade >= 1800:
                raise semJuvenilidade
        except:
            raise semJuvenilidade

    def set_dia(self, dia_str = None, inicio_ciclo = None):
        try:
            self.data = list(map(int, dia_str.split("/")))
        except:
            raise semData
        try:
            if len(self.data) == 3:
                self.data = datetime.datetime(day = self.data[0], month = self.data[1], year = self.data[2])
            elif len(self.data) == 2:
                self.data = datetime.datetime(day = self.data[0], month = self.data[1], year = datetime.datetime.today().year)
        except:
            raise semData
        self.dias_meses = [calendar.monthrange(self.data.year, x)[1] for x in range(1, 13)]
        inicio_mes = [0]
        inicio_mes.extend(self.dias_meses[:11])
        self.NDA = self.data.timetuple().tm_yday
        self.inicio_ciclo = inicio_ciclo
        self.historico = False if self.data.year >= datetime.datetime.today().year-1 else True

    def get_dados(self):
        if self.data is None or self.historico is None:
            raise semData
        elif self.local is None or self.local == "":
            raise semLocal
        try: 
            dados = requests.get('https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?request=execute&identifier=SinglePoint&parameters=T2M,T2M_MAX,T2M_MIN,PRECTOT&userCommunity=AG&tempAverage={2}&outputList=JSON&lat={0}&lon={1}&user=anonymous'.format(self.local.latitude, self.local.longitude, "CLIMATOLOGY" if self.historico == False else "DAILY&startDate={0}{1}{2}&endDate={3}{1}{2}".format(self.data.year-2, self.data.month, self.data.day, min(self.data.year+2, datetime.datetime.today().year-1))))
            features = json.loads(dados.text)["features"][0]
            properties = features["properties"]
            parameter = properties["parameter"]

            self.dados = pd.DataFrame(data=parameter)
            if self.historico == False:
                self.dados["Mes"] = [int(x) for x in self.dados.index]
                self.dados = self.dados.sort_values(by = "Mes")
                self.dados = self.dados.drop(self.dados.index[12])
        except:
            raise semDados

    def atualizar_n_dias(self):
        self.dias_meses = [calendar.monthrange(self.data_final.year, x)[1] for x in range(1, 13)]
        self.n_dias = sum(self.dias_meses) if self.historico == False else min(self.temperaturas.size, self.chuvas.size)

    def atualizar_planilhas(self):
       self.atualizar_n_dias()
       self.temperaturas = np.repeat(self.dados["T2M"].values, self.dias_meses) if self.historico == False else self.dados["T2M"].values
       self.chuvas = np.repeat(self.dados["PRECTOT"].values, self.dias_meses) if self.historico == False else self.dados["PRECTOT"].values

    def calcular_graus_dias(self):
        if self.dados is None:
            self.get_dados()
        elif self.dias_meses is None or self.data is None or self.historico is None or self.inicio_ciclo is None:
            raise semData
        elif self.juvenilidade is None:
            self.set_juvenilidade(0)
        self.data_final = self.data
        data_str = "".join(list(map(lambda x: ("0" if x < 10 else "") + str(x), [self.data_final.year, self.data_final.month, self.data_final.day])))
        self.NDA_final = self.NDA if self.historico == False else self.dados.index.get_loc(data_str)
        self.temperaturas = np.repeat(self.dados["T2M"].values, self.dias_meses) if self.historico == False else self.dados["T2M"].values
        self.chuvas = np.repeat(self.dados["PRECTOT"].values, self.dias_meses) if self.historico == False else self.dados["PRECTOT"].values
        self.atualizar_n_dias()
        # Adicionar a juvenilidade se for calcular o fim do ciclo (início do ciclo for fornecido)
        if self.juvenilidade > 0 and self.inicio_ciclo == True:
            if self.historico == True:
                self.NDA_final += self.juvenilidade
                self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
            elif self.historico == False:
                self.data_final = self.data_final + datetime.timedelta(self.juvenilidade)
                self.NDA_final = self.data_final.timetuple().tm_yday
            self.atualizar_planilhas()
        try:
            soma_chuva = 0
            self.cumsum_chuva = []
            soma_temp = 0
            self.cumsum_temp = []
            if self.inicio_ciclo == False:
                # Se o fim do ciclo for fornecido, primeiro desconta-se o tempo do fim do ciclo
                # até a poda
                if self.historico == False:
                    self.data_final = self.data_final - datetime.timedelta(self.cultura["tempo"].tolist()[0])
                    self.NDA_final = self.data_final.timetuple().tm_yday
                else:
                    self.NDA_final -= self.cultura["tempo"].tolist()[0]
                    self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
                self.atualizar_planilhas()
                if self.NDA_final < 0 and self.historico == True:
                    raise semCalculo
                # A seguir, desconta-se os dias para acumular a quantidade de chuva necessária para florescer
                while soma_chuva < self.cultura["chuva"].tolist()[0]:
                    # Adiciona os dias que passaram à lista de dias
                    soma_chuva += self.chuvas[self.NDA_final - 1 if self.historico == False else 0]
                    self.cumsum_chuva.append(soma_chuva)
                    if self.historico == False:
                        self.data_final = self.data_final - datetime.timedelta(1)
                        self.NDA_final = self.data_final.timetuple().tm_yday
                    else:
                        self.NDA_final -= 1
                        self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
                    self.atualizar_planilhas()
                if self.NDA_final < 0 and self.historico == True:
                    raise semCalculo
                # Então, considerando a soma de graus dias
                while soma_temp < self.cultura["graus_dias"].tolist()[0]:
                    soma_temp += max(float(self.temperaturas[self.NDA_final - 1 if self.historico == False else 0]) - float(self.cultura["tbase"].tolist()[0]), 0)
                    self.cumsum_temp.append(soma_temp)
                    if self.historico == False:
                        self.data_final = self.data_final - datetime.timedelta(1)
                        self.NDA_final = self.data_final.timetuple().tm_yday
                    else:
                        self.NDA_final -= 1
                        self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
                    self.atualizar_planilhas()
                if self.NDA_final < 0 and self.historico == True:
                    raise semCalculo
            # Se for fornecida a data de início do ciclo
            elif self.inicio_ciclo == True:
                # Primeiro calcula-se os graus-dias
                while soma_temp < self.cultura["graus_dias"].tolist()[0]:
                    diferenca = float(self.temperaturas[self.NDA_final - 1 if self.historico == False else 0])-float(self.cultura["tbase"].tolist()[0])
                    soma_temp += max(diferenca, 0)
                    self.cumsum_temp.append(soma_temp)
                    if self.historico == False:
                        self.data_final = self.data_final + datetime.timedelta(1)
                        self.NDA_final = self.data_final.timetuple().tm_yday
                    else:
                        self.NDA_final += 1
                        self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
                    self.atualizar_planilhas()
                if self.NDA_final < 0 and self.historico == True:
                    raise semCalculo
                # Então, a chuva
                while soma_chuva < self.cultura["chuva"].tolist()[0]:
                    soma_chuva += self.chuvas[self.NDA_final - 1 if self.historico == False else 0]
                    self.cumsum_chuva.append(soma_chuva)
                    if self.historico == False:
                        self.data_final = self.data_final + datetime.timedelta(1)
                        self.NDA_final = self.data_final.timetuple().tm_yday
                    else:
                        self.NDA_final += 1
                        self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
                    self.atualizar_planilhas()
                if self.NDA_final < 0 and self.historico == True:
                    raise semCalculo
                # E, a seguir, adiciona o tempo entre até a colheita
                if self.historico == False:
                    self.data_final = self.data_final + datetime.timedelta(self.cultura["tempo"].tolist()[0])
                    self.NDA_final = self.data_final.timetuple().tm_yday
                else:
                    self.NDA_final += self.cultura["tempo"].tolist()[0]
                    self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
                self.atualizar_planilhas()
                if self.NDA_final < 0 and self.historico == True:
                    raise semCalculo
        except:
            raise semCalculo
        # Calcular a juvenilidade caso tenha sido fornecida a data do final do ciclo
        if self.juvenilidade > 0 and self.inicio_ciclo == False:
            if self.historico == True:
                self.NDA_final -= self.juvenilidade
                self.data_final = datetime.datetime(day = int(self.dados.index[self.NDA_final][6:8]), month = int(self.dados.index[self.NDA_final][4:6]), year = int(self.dados.index[self.NDA_final][0:4]))
            elif self.historico == False:
                self.data_final = self.data_final - datetime.timedelta(self.juvenilidade)
                self.NDA_final = self.data_final.timetuple().tm_yday
            self.atualizar_planilhas()
            if self.NDA_final < 0 and self.historico == True:
                raise semCalculo
