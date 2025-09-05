import math
import sys
from contextlib import redirect_stdout
import matplotlib.pyplot as plt

from DE.DiffEvolution import main as DE
from GA.Genetic import main as GA
from PSO.ParticleSwarm import main as PSO
from AC.AntColony import main as AC
from ABC.BeeColony import main as ABC
from GeradorComponentes import main as GeradorComponentes
from GeradorIndividuos import main as GeradorIndividuos

def main():
    def truncate(number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

    # Variáveis para geração de componentes e individuos
    confiabilidade_minima = 0.8
    confiabilidade_maxima = 0.9
    lim_sup_peso = 20
    lim_inf_peso = 5
    lim_sup_custo = 15
    lim_inf_custo = 4
    num_tipos_componentes = 15
    num_individuos = 50
    num_variaveis = 5
    num_max_componentes_subsistema = 3
    num_min_componentes_subsistema = 1
    coeficiente_custo = 1.1
    coeficiente_peso = 1.05

    # Variáveis para execução do algoritmo
    num_geracoes = 100
    peso_max = 50
    custo_max = 30

    componentes = GeradorComponentes(
        num_tipos_componentes,
        confiabilidade_maxima,
        confiabilidade_minima,
        lim_inf_custo,
        lim_sup_custo,
        lim_inf_peso,
        lim_sup_peso
    )

    individuos = GeradorIndividuos(
        num_tipos_componentes,
        num_individuos,
        num_variaveis,
        num_max_componentes_subsistema,
        num_min_componentes_subsistema,
        peso_max,
        custo_max,
        componentes, 
        coeficiente_custo, 
        coeficiente_peso
    )

    for i in range(len(individuos)):
        print("Individuo {}:".format(i))
        print(individuos[i])

    print("")

    for i in range(componentes.shape[1]):
        print("Componente {}:".format(i))
        print("Confiabilidade: {}".format(componentes[0][i]))
        print("Custo: {}".format(componentes[1][i]))
        print("Peso: {}\n".format(componentes[2][i]))

    # Executa GA e captura os resultados
    with open('./GA/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_GA, melhor_valor_GA, melhor_individuo_GA, geracao_GA = GA(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
        finally:
            sys.stdout = sys.__stdout__

    # Executa PSO e captura os resultados
    with open('./PSO/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_PSO, melhor_valor_PSO, melhor_individuo_PSO, geracao_PSO = PSO(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
        finally:
            sys.stdout = sys.__stdout__

    # Executa DE e captura os resultados
    with open('./DE/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_DE, melhor_valor_DE, melhor_individuo_DE, geracao_DE = DE(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
        finally:
            sys.stdout = sys.__stdout__

    # Executa AntColony e captura os resultados
    '''with open('./AC/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_AC, melhor_valor_AC = AC(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
        finally:
            sys.stdout = sys.__stdout__'''
    
    # Executa Artificial Bee Colony e captura os resultados
    with open('./ABC/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_ABC, melhor_valor_ABC, melhor_individuo_ABC, geracao_ABC = ABC(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
        finally:
            sys.stdout = sys.__stdout__


    # Gerando o gráfico comparativo
    plt.plot(range(1, len(solucoes_PSO) + 1), solucoes_PSO, label='PSO ({})'.format(melhor_valor_PSO), color='purple')
    plt.plot(range(1, len(solucoes_DE) + 1), solucoes_DE, label='DE ({})'.format(melhor_valor_DE), color='green')
    plt.plot(range(1, len(solucoes_GA) + 1), solucoes_GA, label='GA ({})'.format(melhor_valor_GA), color='orange')
    #plt.plot(range(1, len(solucoes_AC) + 1), solucoes_AC, label='ACO ({})'.format(melhor_valor_AC), color='blue')
    plt.plot(range(1, len(solucoes_ABC) + 1), solucoes_ABC, label='ABC ({})'.format(melhor_valor_ABC), color='red')

    plt.xlabel('Geração')
    plt.ylabel('log(Função Objetivo)')
    plt.title('Comparação dos Algoritmos')
    plt.legend()
    plt.grid(True)

    penalidade_GA = truncate(melhor_individuo_GA.valor_funcao_objetivo - melhor_individuo_GA.confiabilidade_total, 8)
    textoGA = "GA\nAlcançado na geração: " + str(geracao_GA) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_GA.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_GA.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_GA) + "\nCusto: " + str(melhor_individuo_GA.custo) + "\nPeso: " + str(melhor_individuo_GA.peso)
    plt.figtext(0.15, 0.029, textoGA, wrap=True, horizontalalignment='center', fontsize=8)

    penalidade_PSO = truncate(melhor_individuo_PSO.valor_funcao_objetivo - melhor_individuo_PSO.confiabilidade_total, 8)
    textoPSO = "PSO\nAlcançado na geração: " + str(geracao_PSO) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_PSO.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_PSO.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_PSO) + "\nCusto: " + str(melhor_individuo_PSO.custo) + "\nPeso: " + str(melhor_individuo_PSO.peso)
    plt.figtext(0.4, 0.029, textoPSO, wrap=True, horizontalalignment='center', fontsize=8)

    penalidade_DE = truncate(melhor_individuo_DE.valor_funcao_objetivo - melhor_individuo_DE.confiabilidade_total, 8)
    textoDE = "DE\nAlcançado na geração: " + str(geracao_DE) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_DE.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_DE.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_DE) + "\nCusto: " + str(melhor_individuo_DE.custo) + "\nPeso: " + str(melhor_individuo_DE.peso)
    plt.figtext(0.68, 0.029, textoDE, wrap=True, horizontalalignment='center', fontsize=8)

    '''penalidade_AC = truncate(melhor_valor_AC - melhor_valor_AC, 8)
    textoAC = "ACO\nAlcançado na geração: " + str(num_geracoes) + "\nFunção Objetivo: " + str(truncate(melhor_valor_AC, 8)) + "\nConfiabilidade: " + str(truncate(melhor_valor_AC, 8)) + "\nPenalidade: " + str(penalidade_AC) + "\nCusto: " + str(melhor_valor_AC) + "\nPeso: " + str(melhor_valor_AC)
    plt.figtext(0.87, 0.029, textoAC, wrap=True, horizontalalignment='center', fontsize=8)'''

    penalidade_ABC = truncate(melhor_valor_ABC - melhor_valor_ABC, 8)
    textoAC = "ACO\nAlcançado na geração: " + str(num_geracoes) + "\nFunção Objetivo: " + str(truncate(melhor_valor_ABC, 8)) + "\nConfiabilidade: " + str(truncate(melhor_valor_ABC, 8)) + "\nPenalidade: " + str(penalidade_ABC) + "\nCusto: " + str(melhor_valor_ABC) + "\nPeso: " + str(melhor_valor_ABC)
    plt.figtext(0.87, 0.029, textoAC, wrap=True, horizontalalignment='center', fontsize=8)

    # Ajustes finais e salvamento
    plt.subplots_adjust(bottom=0.2)
    plt.savefig('./comparativeMethods.png')
    plt.show()

if __name__ == "__main__":
    with open('components.txt', 'w') as f:
        with redirect_stdout(f):
            main()