# GrausDias
Cálculo de graus-dias

[Clique aqui para assistir o video](https://www.youtube.com/watch?v=3jiStOZZZII)

No momento, a ferramenta funciona em distribuições Linux com Python3 e os módulos geopy.geocoder, pandas, numpy, matplotlib e tkinter instalados.

A partir da data de início/fim de um estádio fenológico de alguma cultura inserida e do local onde o plantio deve ser realizado, é possvel calcular a soma de graus-dias até atingir a constante térmica, utilizando dados meteorológicos do NASA Power.

Para inserir uma nova cultura, é necessário informar a temperatura basal, a constante térmica, a quantidade de chuva necessária, se houver, e o número de dias necessários, se houver, para completar um determinado estádio do desenvolvimento.

No arquivo frutiferas.csv, são armazenados os dados das culturas inseridas no programa.
O programa gera um arquivo grafico.png, gerado pelo matplotlib, com o desenvolvimento da cultura em determinado local.
No arquivo gui.log, podem ser acessados eventuais erros do programa.
Além disso, através do arquivo ciclos.csv, podem ser comparados os dados de diferentes simulações rodadas pelo programa.
