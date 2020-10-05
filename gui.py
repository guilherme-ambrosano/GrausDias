import importlib
import os.path
import traceback
import datetime
import gc
import datepicker
import tkinter
from tkinter import messagebox
from tkinter import Frame
from tkinter import ttk
from classe_planilha import *
import grafico
from PIL import ImageTk, Image


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

plan = planilha()
top = tkinter.Tk()
top.geometry("500x400")
top.title("Cálculo de Graus-Dias")
top.resizable(0, 0)
main = Frame(top, pady = 15, padx = 15)
main.pack(expand = True, fill = "both")

if not os.path.isfile("ciclos.csv"):
    with open(os.path.join(__location__, "ciclos.csv"), "w+") as f:
        f.write("Cultura,Local,Latitude,Longitude,Data do início do período,Temperatura média,Número de dias no período\n")

semeadura = True
Sul = True
Oeste = True
nome = tkinter.StringVar()
sem_ou_colh = tkinter.StringVar()
hemisferio_lat = tkinter.StringVar()
hemisferio_lat.set("S" if Sul == True else "N")
hemisferio_lon = tkinter.StringVar()
hemisferio_lon.set("O" if Oeste == True else "L")
sem_ou_colh.set("Fim do período" if semeadura == True else "Início do período")

data_colheita = None
data_sem_colh = tkinter.StringVar()
data_sem_colh.set("Início do período:" if semeadura == True else "Fim do período:")

open("gui.log", 'w').close()

def updateHemisferio_lat():
    global Sul
    global hemisferio_lat
    Sul = False if Sul == True else True
    hemisferio_lat.set("S" if Sul == True else "N")

def updateHemisferio_lon():
    global Oeste
    global hemisferio_lon
    Oeste = False if Oeste == True else True
    hemisferio_lon.set("O" if Oeste == True else "L")

def update_sem_colh():
    global semeadura
    global data_sem_colh
    semeadura = True if semeadura == False else False
    sem_ou_colh.set("Fim do período" if semeadura == True else "Início do período")
    data_sem_colh.set("Início do período:" if semeadura == True else "Fim do período:")

def erro_sem_calculo():
    messagebox.showinfo("Erro", "Desculpe, não foi possível realizar os cálculos.")
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    raise semCalculo

def erro_sem_local():
    messagebox.showinfo("Erro", "Local inválido.")
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    raise semLocal
    
def erro_sem_cultura():
    messagebox.showinfo("Erro", "Cultura não encontrada.")
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    raise semCultura

def erro_sem_data():
    messagebox.showinfo("Erro", "Data inválida.")
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    raise semData

def erro_sem_dados():
    messagebox.showinfo("Erro", "Não foi possível obter os dados.")
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    raise semDados

dia = mes = ano = 0

def erro_juvenilidade():
    global juvenilidade
    global entry_tempo
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    if juvenilidade.get() == 1 and entry_tempo.get().strip() == "":
        messagebox.showinfo("Erro", "Tempo de juvenilidade inválido.")
    elif juvenilidade.get() == 1 and (int(str(entry_tempo.get().strip()).replace(",", ".")) < 0 or int(str(entry_tempo.get().strip()).replace(",", ".")) > 1800):
        messagebox.showinfo("Erro", "Tempo de juvenilidade inválido.")

def erro_conexao():
    messagebox.showinfo("Erro", "Não foi possível se conectar à internet.")
    with open("gui.log", "a") as file:
       file.write(traceback.format_exc())
    raise semConexao

def dividir_string(string, w):
    l = len(string)
    if l > w:
        lista = string.split(" ")
        soma = 0
        soma_cum = [0]
        for s in lista:
            soma += len(s)
            soma += 1
            soma_cum.append(soma)
        soma_cum = [x%w for x in soma_cum]
        nova_string = lista[0]
        for i in range(1, len(lista)):
            if soma_cum[i] >= soma_cum[i-1] and i != len(lista):
                nova_string = nova_string + lista[i] + " "
            elif soma_cum[i] < soma_cum[i-1] and i != len(lista):
                nova_string = nova_string + lista[i] + "\n"
            elif i == len(lista):
                nova_string = nova_string + lista[i]
        return nova_string
    else:
        return string

def fechar_resultado():
    global janela_resultado
    janela_resultado.quit()
    janela_resultado.destroy()

def janelaResultado():
    global semeadura, plan, janela_resultado
    janela_resultado = tkinter.Toplevel()
    try:
        resultado_local = "Local: {0}".format(dividir_string(plan.local.address, 50))
        resultado_coord = "Lat: {0}, Lon: {1}".format(str(round(plan.local.latitude, 2)).replace(".", ","), str(round(plan.local.longitude, 2)).replace(".",","))
    except:
        janela_resultado.destroy()
        erro_sem_local()
    janela_resultado.geometry("720x{0}".format(640+10*resultado_local.count("\n")))
    janela_resultado.title("Resultado")
    janela_resultado.resizable(0, 0)
    resultado_data_inicial = "{0} {1}".format("   Data do fim do período:" if plan.inicio_ciclo == False else "Data do início do período:", str(plan.data.day) + "/" + str(plan.data.month) + "/" + str(plan.data.year))
    resultado = "O " + ("início" if semeadura == False else "fim") + (" do período deverá ser" if semeadura == False else " do período será") + " no dia {0}/{1}/{2}".format(plan.data_final.day, plan.data_final.month, plan.data_final.year)
    label_data = tkinter.Label(janela_resultado, text = resultado_data_inicial)
    label_data.place(x = 440 if semeadura == False else 30, y = 30)
    label_local = tkinter.Label(janela_resultado, text = resultado_local)
    label_local.place(x = 160, y = 550)
    label_coord = tkinter.Label(janela_resultado, text = resultado_coord)
    label_coord.place(x = 270, y = 580 + 10*resultado_local.count("\n"))
    label_resultado = tkinter.Label(janela_resultado, text = resultado)
    label_resultado.place(x = 440 if semeadura == True else 30, y = 30)
    img = ImageTk.PhotoImage(Image.open("grafico.png"))
    panel = tkinter.Label(janela_resultado, image = img)
    panel.place(x = 40, y = 60)
    botao_fechar_resultado = tkinter.Button(janela_resultado, text = "Fechar", command = fechar_resultado)
    botao_fechar_resultado.place(x = 30, y = 590+10*resultado_local.count("\n"))
    janela_resultado.mainloop()

def ir(event = None):
    global janela_cultura, janela_resultado
    global plan
    global data
    global data_colheita
    global entry_local
    global menu_nome
    global coord, entry_lat, entry_lat_minutos, entry_lat_segundos
    global entry_lon, entry_lon_minutos, entry_lon_segundos
    global Oeste, Sul
    global semeadura
    global juvenilidade
    global entry_tempo
    global dia, mes, ano

    try:
        try:
            if janela_cultura.winfo_exists() == 1:
                janela_cultura.destroy()
        except NameError:
            pass
        try:
            if janela_resultado.winfo_exists() == 1:
                janela_resultado.quit()
                janela_resultado.destroy()
        except NameError:
            pass
        data_colheita = data.get().strip()
        local = entry_local.get().strip()
        cultura = menu_nome.get()
        tempo = entry_tempo.get().strip()
        lat = entry_lat.get().replace(",", ".").strip()
        lon = entry_lon.get().replace(",", ".").strip()
        lat_minutos = entry_lat_minutos.get().replace(",", ".").strip()
        lat_segundos = entry_lat_segundos.get().replace(",", ".").strip()
        lon_minutos = entry_lon_minutos.get().replace(",", ".").strip()
        lon_segundos = entry_lon_segundos.get().replace(",", ".").strip()

        splash = tkinter.Toplevel()
        splash.title("Cálculo em andamento...")
        splash.geometry("500x100")
        splash.resizable(0, 0)
        ano_atual = datetime.datetime.today().year
        try:
            plan.set_dia(data_colheita, semeadura)
        except:
            splash.destroy()
            erro_sem_data()
        label = tkinter.Label(splash, text = "Coletando dados {} do NASA Power...".format("históricos" if plan.historico == True else "médios"))
        label.place(x = 115, y = 40)
        splash.update_idletasks()
        try:
            if coord.get() == 1:
                lat_minutos = 0 if lat_minutos == "" else lat_minutos
                lon_minutos = 0 if lon_minutos == "" else lon_minutos
                lat_segundos = 0 if lat_segundos == "" else lat_segundos
                lon_segundos = 0 if lon_segundos == "" else lon_segundos
                lat_dada = (-1 if Sul == True else 1)*(float(lat) + float(lat_minutos)/60 + float(lat_segundos)/3600)
                lon_dada = (-1 if Oeste == True else 1)*(float(lon) + float(lon_minutos)/60 + float(lon_segundos)/3600)
                plan.set_local(None, lat_dada, lon_dada)
            else:
                plan.set_local(local)
            plan.set_cultura(cultura)
            plan.set_juvenilidade(int(str(tempo).replace(",", ".")) if juvenilidade.get() == 1 else 0)
            plan.get_dados()
            plan.calcular_graus_dias()
            grafico.fazer_grafico(plan)
            splash.destroy()
            lista_resultado = [plan.cultura["nome"].tolist()[0], plan.local.address.replace(",", ""), round(plan.local.latitude,2), round(plan.local.longitude,2), (plan.data.strftime("%d/%m/%Y") if semeadura == True else plan.data_final.strftime("%d/%m/%Y")), round((plan.cumsum_temp[-1] + len(plan.cumsum_temp)*plan.cultura["tbase"].tolist()[0])/len(plan.cumsum_temp), 2), len(plan.dias)]
            lista_resultado = list(map(str, lista_resultado))
            with open("ciclos.csv", "a") as f:
                f.write(",".join(lista_resultado)+"\n")
            janelaResultado()
        except (semLocal, ValueError, AttributeError) as e:
            print(traceback.format_exc())
            splash.destroy()
            erro_sem_local()
        except semCultura:
            splash.destroy()
            erro_sem_cultura()
        except semData:
            splash.destroy()
            erro_sem_data()
        except semDados:
            splash.destroy()
            erro_sem_dados()
        except semConexao:
            splash.destroy()
            erro_conexao()
        except semJuvenilidade:
            splash.destroy()
            erro_juvenilidade()
        except semCalculo:
            splash.destroy()
            erro_sem_calculo()
        except ValueError:
            splash.destroy()
            erro_juvenilidade()
    except:
        with open("gui.log", "a") as file:
           file.write(traceback.format_exc())

        pass

def updateJuvenil():
    global juvenilidade
    global entry_tempo
    if juvenilidade.get() == 1:
        entry_tempo.config(state=tkinter.NORMAL)
    elif juvenilidade.get() == 0:
        entry_tempo.config(state=tkinter.DISABLED)

def updateLocal():
    global coord
    global entry_lat, entry_lat_minutos, entry_lat_segundos, entry_lon, entry_local, botao_lon_hemisferio, botao_lat_hemisferio
    if coord.get() == 1:
        entry_lon.config(state=tkinter.NORMAL)
        entry_lon_minutos.config(state=tkinter.NORMAL)
        entry_lon_segundos.config(state=tkinter.NORMAL)
        entry_lat.config(state=tkinter.NORMAL)
        entry_lat_minutos.config(state=tkinter.NORMAL)
        entry_lat_segundos.config(state=tkinter.NORMAL)
        botao_lat_hemisferio.config(state=tkinter.NORMAL)
        botao_lon_hemisferio.config(state=tkinter.NORMAL)
        entry_local.config(state=tkinter.DISABLED)
    elif coord.get() == 0:
        entry_lon.config(state=tkinter.DISABLED)
        entry_lon_minutos.config(state=tkinter.DISABLED)
        entry_lon_segundos.config(state=tkinter.DISABLED)
        entry_lat.config(state=tkinter.DISABLED)
        entry_lat_minutos.config(state=tkinter.DISABLED)
        entry_lat_segundos.config(state=tkinter.DISABLED)
        botao_lat_hemisferio.config(state=tkinter.DISABLED)
        botao_lon_hemisferio.config(state=tkinter.DISABLED)
        entry_local.config(state=tkinter.NORMAL)

def cancelar_cultura():
    global janela_cultura
    janela_cultura.destroy()


def update_opcoes():
    global opcoes, menu_nome
    opcoes = plan.frutiferas["nome"].tolist()
    menu_nome['values']=[x for x in opcoes]

class semTemperatura(Exception):
    pass

class semGrausDias(Exception):
    pass

class semChuva(Exception):
    pass

class semTempo(Exception):
    pass

def ir_cultura(event = None):
    global top
    global plan
    global janela_cultura
    global entry_nome, entry_tbase, entry_graus_dias, entry_chuva, entry_tempo_cultura
    try:
        nome_original = str(entry_nome.get())
        frutiferas = pd.read_csv("frutiferas.csv")
        if plan.tirar_acentos(nome_original) in map(plan.tirar_acentos, frutiferas["nome"].tolist()):
            messagebox.showinfo("Erro", "Esta cultura já existe")
            raise semCultura
        if plan.tirar_acentos(nome_original) == "":
            messagebox.showinfo("Erro", "Insira uma cultura válida")
            raise semCultura
        tbase = entry_tbase.get()
        try:
            tbase = float(str(tbase).replace(",", "."))
        except:
            messagebox.showinfo("Erro", "Insira um valor de temperatura válido")
            raise semTemperatura
        graus_dias = entry_graus_dias.get()
        try:
            graus_dias = int(str(graus_dias).replace(",", "."))
        except:
            messagebox.showinfo("Erro", "Insira um valor de graus-dias válido")
            raise semGrausDias
        chuva = entry_chuva.get()
        try:
            chuva = float(str(chuva).replace(",", "."))
        except:
            messagebox.showinfo("Erro", "Insira um valor de chuva válido")
            raise semChuva
        tempo = entry_tempo_cultura.get()
        try:
            tempo = int(str(tempo).replace(",", "."))
        except:
            messagebox.showinfo("Erro", "Insira um valor de tempo válido")
            raise semTempo
        plan.nova_cultura(nome_original, tbase, graus_dias, chuva, tempo)
        update_opcoes()
        janela_cultura.destroy()
    except:
        pass


def criarCultura():
    global plan
    global janela_cultura
    global entry_nome, entry_tbase, entry_graus_dias, entry_chuva, entry_tempo_cultura
    janela_cultura = tkinter.Toplevel()
    janela_cultura.geometry("450x400")
    janela_cultura.title("Criar nova cultura")
    janela_cultura.resizable(0, 0)
    label_nome = tkinter.Label(janela_cultura, text = "Nome da cultura:")
    label_nome.place(x = 40, y = 50)
    label_tbase = tkinter.Label(janela_cultura, text = "Temperatura base (\u2103):")
    label_tbase.place(x = 40, y = 100)
    label_graus_dias = tkinter.Label(janela_cultura, text = "Graus-dias necessários:", justify = tkinter.LEFT)
    label_graus_dias.place(x = 40, y = 150)
    label_chuva = tkinter.Label(janela_cultura, text = "Chuva total necessária (mm):", justify = tkinter.LEFT)
    label_chuva.place(x = 40, y = 200)
    label_tempo = tkinter.Label(janela_cultura, text = "Tempo final (dias):", justify = tkinter.LEFT)
    label_tempo.place(x = 40, y = 250)
    entry_nome = tkinter.Entry(janela_cultura)
    entry_nome.place(x = 245, y = 50)
    entry_tbase = tkinter.Entry(janela_cultura)
    entry_tbase.place(x = 245, y = 100)
    entry_graus_dias = tkinter.Entry(janela_cultura)
    entry_graus_dias.place(x = 245, y = 150)
    entry_chuva = tkinter.Entry(janela_cultura)
    entry_chuva.place(x = 245, y = 200)
    entry_tempo_cultura = tkinter.Entry(janela_cultura)
    entry_tempo_cultura.place(x = 245, y = 250)
    botao_cancelar_cultura = tkinter.Button(janela_cultura, text = "Cancelar", command = cancelar_cultura)
    botao_cancelar_cultura.place(x = 20, y = 330)
    botao_ir_cultura = tkinter.Button(janela_cultura, text = "Criar", command = ir_cultura)
    botao_ir_cultura.place(x = 370, y = 330)
    janela_cultura.mainloop()

def fechar():
    global top, janela_resultado
    try:
        if janela_resultado.winfo_exists() == 1:
            janela_resultado.quit()
            janela_resultado.destroy()
        top.quit()
    except:
        top.quit()

label_data = tkinter.Label(top, textvariable = data_sem_colh)
label_data.place(x = 30, y = 50)
data = datepicker.Datepicker(main)
data.place(x = 135, y = 37)

def direita(event):
    global data
    if data.is_calendar_visible:
        data.calendar_frame.select_next_day()
        data.icursor(tkinter.END)
        return "break"

def esquerda(event):
    global data
    if data.is_calendar_visible:
        data.calendar_frame.select_prev_day()
        data.icursor(tkinter.END)
        return "break"

def fechar_calendario(event):
    global data
    if data.is_calendar_visible:
        data.set_date_from_calendar()
        data.hide_calendar()
        return "break"

data.bind("<Right>", direita)
data.bind("<Left>", esquerda)
data.bind("<Return>", fechar_calendario)

butao_sem_colh = tkinter.Button(top, textvariable = sem_ou_colh, command = update_sem_colh)
butao_sem_colh.place(x = 340, y = 50)

juvenilidade = tkinter.IntVar()
juvenil_check = tkinter.Checkbutton(top, text = "Juvenilidade", variable = juvenilidade, command = updateJuvenil)
juvenil_check.place(x = 20, y = 100)

label_tempo = tkinter.Label(top, text = "Tempo (dias):")
label_tempo.place(x = 150, y = 100)
entry_tempo = tkinter.Entry(top, state= tkinter.DISABLED)
entry_tempo.place(x = 250, y = 100)

label_local = tkinter.Label(top, text = "Local:")
label_local.place(x = 30, y = 150)
entry_local = tkinter.Entry(top)
entry_local.place(x = 80, y = 150)

coord = tkinter.IntVar()
check_coordenadas = tkinter.Checkbutton(top, text = "Inserir coordenadas", variable = coord, command = updateLocal)
check_coordenadas.place(x = 280, y = 150)

label_lat = tkinter.Label(top, text = "Lat:")
label_lat.place(x = 30, y = 200)
entry_lat = tkinter.Entry(top, state=tkinter.DISABLED, width = 3)
entry_lat.place(x = 65, y = 200)
label_lat_graus = tkinter.Label(top, text = "\u00b0")
label_lat_graus.place(x = 97, y = 200)
entry_lat_minutos = tkinter.Entry(top, state=tkinter.DISABLED, width = 3)
entry_lat_minutos.place(x = 108, y = 200)
label_lat_minutos = tkinter.Label(top, text = "'")
label_lat_minutos.place(x = 140, y = 200)
entry_lat_segundos = tkinter.Entry(top, state=tkinter.DISABLED, width = 3)
entry_lat_segundos.place(x = 150, y = 200)
label_lat_segundos = tkinter.Label(top, text = "''")
label_lat_segundos.place(x = 180, y = 200)
botao_lat_hemisferio = tkinter.Button(top, textvariable = hemisferio_lat, command = updateHemisferio_lat, width = 1, state = tkinter.DISABLED)
botao_lat_hemisferio.place(x = 190, y = 198)

label_lon = tkinter.Label(top, text = "Long:")
label_lon.place(x = 250, y = 200)
entry_lon = tkinter.Entry(top, state=tkinter.DISABLED, width = 4)
entry_lon.place(x = 291, y = 200)
label_lon_graus = tkinter.Label(top, text = "\u00b0")
label_lon_graus.place(x = 330, y = 200)
entry_lon_minutos = tkinter.Entry(top, state=tkinter.DISABLED, width = 3)
entry_lon_minutos.place(x = 343, y = 200)
label_lon_minutos = tkinter.Label(top, text = "'")
label_lon_minutos.place(x = 376, y = 200)
entry_lon_segundos = tkinter.Entry(top, state=tkinter.DISABLED, width = 3)
entry_lon_segundos.place(x = 385, y = 200)
label_lon_segundos = tkinter.Label(top, text = "''")
label_lon_segundos.place(x = 415, y = 200)
botao_lon_hemisferio = tkinter.Button(top, textvariable = hemisferio_lon, command = updateHemisferio_lon, width = 1, state = tkinter.DISABLED)
botao_lon_hemisferio.place(x = 425, y = 198)

opcoes = plan.frutiferas["nome"].tolist()
nome.set(opcoes[0])
menu_nome = ttk.Combobox(top, values = [x for x in opcoes])
menu_nome.place(x = 90, y = 250)
label_cultura = tkinter.Label(top, text = "Cultura:")
label_cultura.place(x = 30, y = 250)
butao_cultura = tkinter.Button(top, text = "Criar nova", command = criarCultura)
butao_cultura.place(x = 365, y = 250)

butao_fechar = tkinter.Button(top, text = "Sair", command = fechar)
butao_fechar.place(x = 20, y = 330)

butao_ir = tkinter.Button(top, text = "Ir!", command = ir)
butao_ir.place(x = 420, y = 330)

top.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())
top.unbind_class("Button", "<Key-space>")

top.mainloop()
