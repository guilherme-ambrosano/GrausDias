import classe_planilha
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import pandas as pd
import datetime

def formatar_dias_datetime(data):
    dia = data.day
    mes = data.month
    ano = data.year
    final = str(dia)+"/"+str(mes)+"/"+str(ano)
    return final

def fazer_grafico(teste):
    temperaturas = []
    chuvas = []
    juvenilidade = []
    tempo = []
    
    breaks_eixo = []
    
    for i in range(teste.juvenilidade):
        if i == 0:
            breaks_eixo.append(1)
        else:
            breaks_eixo.append(0)
        temperaturas.append(0)
        chuvas.append(0)
        tempo.append(0)
        juvenilidade.append(i+1)
    for i in range(len(teste.cumsum_temp)):
        if i == 0:
            breaks_eixo.append(1)
        else:
            breaks_eixo.append(0)
        temperaturas.append(teste.cumsum_temp[i])
        chuvas.append(0)
        juvenilidade.append(max(juvenilidade) if juvenilidade != [] else 0)
        tempo.append(0)
    for i in range(len(teste.cumsum_chuva)):
        if i == 0 and teste.cultura["chuva"].tolist()[0]>0:
            breaks_eixo.append(1)
        else:
            breaks_eixo.append(0)
        chuvas.append(teste.cumsum_chuva[i])
        temperaturas.append(max(temperaturas))
        juvenilidade.append(max(juvenilidade) if juvenilidade != [] else 0)
        tempo.append(0)
    for i in range(teste.cultura["tempo"].tolist()[0]):
        if i == 0:
            breaks_eixo.append(1)
        else:
            breaks_eixo.append(0)
        temperaturas.append(max(temperaturas))
        chuvas.append(max(chuvas))
        juvenilidade.append(max(juvenilidade) if juvenilidade != [] else 0)
        tempo.append(i+1)

    base = teste.data
    if teste.inicio_ciclo == True:
        dias = [base + datetime.timedelta(x) for x in range(int(sum([len(juvenilidade), len(temperaturas), len(chuvas), len(tempo)])/4))]
    else:
        dias = [base - datetime.timedelta(x) for x in range(int(sum([len(juvenilidade), len(temperaturas), len(chuvas), len(tempo)])/4))]
        dias = dias[::-1]
    dias = list(map(formatar_dias_datetime, dias))
    teste.dias = dias
     
    
    breaks_eixo[0] = 1
    breaks_eixo[len(breaks_eixo) -1] = 1
    breaks_eixo = [i for i,x in enumerate(breaks_eixo) if x == 1]
    dic_dados = {
            "dias": dias,
            "temperaturas": temperaturas,
            "chuvas": chuvas,
            "juvenilidade": juvenilidade,
            "tempo": tempo}
    
    df = pd.DataFrame.from_dict(dic_dados)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    ax3 = ax.twinx()
    ax4 = ax.twinx()
    
    width = 1

    df.plot(x = "dias", y = "juvenilidade", kind='bar', color='green', ax=ax, width=width, position=0.5, legend = False, rot = 90)
    df.plot(x = "dias", y = "temperaturas", kind='bar', color='red', ax=ax2, width=width, position=0.5, legend = False, rot = 90)
    if teste.cultura["chuva"].tolist()[0] > 0:
        df.plot(x = "dias", y = "chuvas", kind='bar', color='blue', ax=ax3, width=width, position=0.5, legend = False, rot = 90)
    df.plot(x = "dias", y = "tempo", kind='bar', color='orange', ax=ax4, width=width, position=0.5, legend = False, rot = 90)
    
    ax3.set_ylabel('Precipitação (mm)')

    if teste.cultura["chuva"].tolist()[0] <= 0:
        ax3.axis("off")

    ax.yaxis.tick_right()
    ax.set_ylabel('Número de dias')
    ax.yaxis.set_label_position("right")
    ax2.yaxis.tick_left()
    ax2.set_ylabel('Graus-dias (\u2103)')
    ax2.yaxis.set_label_position("left")

    if (teste.cultura["tempo"].tolist()[0] > 0 or teste.juvenilidade > 0) and teste.cultura["chuva"].tolist()[0] >0: 
        ax.spines["right"].set_position(('outward', 45))
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        ax.yaxis.set_major_formatter(matplotlib.ticker.OldScalarFormatter())
    elif teste.cultura["tempo"].tolist()[0]> 0 or teste.juvenilidade > 0:
        pass
    else:
        ax.get_yaxis().set_visible(False)
    
    if teste.cultura["tempo"].tolist()[0] > teste.juvenilidade:
        ax.set_ylim(ax4.get_ylim())
    else:
        ax4.set_ylim(ax.get_ylim())
    ax4.axis('off')
    
    if teste.cultura["chuva"].tolist()[0] > 0:
        ax3.plot([0, len(dias)], [teste.cultura["chuva"].tolist()[0], teste.cultura["chuva"].tolist()[0]], ":", color = "blue")
    ax2.plot([0, len(dias)], [teste.cultura["graus_dias"].tolist()[0], teste.cultura["graus_dias"].tolist()[0]], "--", color = "red", label = "Graus-dias necessários")
    patch_gd = mpatches.Patch(color='red', label='Acúmulo de graus-dias')
    patch_precip = mpatches.Patch(color='blue', label='Acúmulo de precipitação')
    patch_juv = mpatches.Patch(color='green', label='Dias de juvenilidade')
    patch_tempo = mpatches.Patch(color='orange', label='Dias até a colheita') 
    patch_prec_nec = mlines.Line2D([], [], color='blue', label='Precipitação necessária', linestyle = ":")
    patch_gd_nec = mlines.Line2D([], [], color='red', label='Graus-dias necessários', linestyle = "--")
    lista_handles = []
    lista_handles.append(patch_gd)
    if teste.cultura["chuva"].tolist()[0] > 0:
        lista_handles.append(patch_precip)
    if teste.juvenilidade > 0:
        lista_handles.append(patch_juv)
    if teste.cultura["tempo"].tolist()[0] > 0:
        lista_handles.append(patch_tempo)
    lista_handles.append(patch_gd_nec)
    if teste.cultura["chuva"].tolist()[0] > 0:
        lista_handles.append(patch_prec_nec)
    lgd = ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.45), ncol=2, handles = lista_handles)

    plt.xticks(breaks_eixo, df.dias[breaks_eixo].tolist())
    ax.set_xlabel("")
    fig.tight_layout(rect = [0, 0.2, 1, 0.95])
    fig.savefig("grafico.png")
