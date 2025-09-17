import numpy as np
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GeradorIndividuos import Individuo

class DifferentialEvolution:
    def __init__(self, componentes, num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        self.num_individuos = len(individuos)
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.passo = 1
        self.CR = 0.6

        self.num_tipos_componentes = num_tipos_componentes
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema

        self.coeficiente_custo = coeficiente_custo
        self.coeficiente_peso = coeficiente_peso

        self.individuos = []
        for i in range(self.num_individuos):
            self.individuos.append(deepcopy(individuos[i]))
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

    def verifica_duplicados(self, populacao):
        # Verifica se existem indivíduos duplicados na população com base na solução
        solucoes_unicas = set()
        populacao_filtrada = []
        
        for individuo in populacao:
            # Convertemos a solução (duas linhas) para tupla de tuplas, que é hashable
            chave_solucao = (tuple(individuo.solucao[0]), tuple(individuo.solucao[1]))
            
            if chave_solucao not in solucoes_unicas:
                solucoes_unicas.add(chave_solucao)
                populacao_filtrada.append(individuo)

        return populacao_filtrada

    def crossover(self, populacao, mutantes):
        novos_candidatos = []
        for i in range(len(populacao)):
            trial_matrix = np.zeros((2, self.num_variaveis), dtype=int)
            for k in range(2):
                l = np.random.randint(0, self.num_variaveis)
                for j in range(self.num_variaveis):
                    r = np.random.rand()
                    if r > self.CR and j != l:
                        trial_matrix[k][j] = populacao[i].solucao[k][j]
                    elif r <= self.CR or j == l:
                        trial_matrix[k][j] = mutantes[i][k][j]
            novos_candidatos.append(trial_matrix)
            
        return novos_candidatos
            

    def mutacao(self, populacao):
        mutantes = []
        for i in range(len(populacao)):

            #gerando 3 indices aleatórios
            idx = [i]
            while len(idx) < 4:
                random_index = np.random.randint(0, len(populacao))
                alreadyExists = False
                for j in range(len(idx)):
                    if idx[j] == random_index:
                        alreadyExists = True
                        break
                if alreadyExists is False:
                    idx.append(random_index)

            #gerando mutante
            mutante = (
                deepcopy(populacao[idx[1]].solucao) + 
                self.passo*(deepcopy(populacao[idx[3]].solucao) - deepcopy(populacao[idx[2]].solucao))
                )

            #correção de parâmetros
            for j in range(self.num_variaveis):
                if mutante[0][j] < 0:
                    mutante[0][j] = 0
                elif mutante[0][j] >= self.num_tipos_componentes:
                    mutante[0][j] = self.num_tipos_componentes - 1
                
                if mutante[1][j] <= 0:
                    mutante[1][j] = 1
                elif mutante[1][j] > self.num_max_componentes_subsistema:
                    mutante[1][j] = self.num_max_componentes_subsistema

            mutantes.append(mutante)
        
        return mutantes
        
    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor


def main(componentes,num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    alg = DifferentialEvolution(componentes,num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    solucoes = []
    solucoes_log = []
    melhor_solucao = -10000
    melhor_solucao_log = -10000
    geracao = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        if i == 0:
            for j in range(alg.num_individuos):
                fit_individuo = alg.individuos[j].valor_funcao_objetivo
                fit_vetor = fit_individuo
                
                if fit_vetor > melhor_solucao:
                    melhor_solucao = fit_vetor
                    melhor_solucao_log = math.log(fit_vetor)
                    
            solucoes.append(melhor_solucao)
            solucoes_log.append(melhor_solucao_log)
            geracao = 0

        mutantes = alg.mutacao(alg.individuos)

        for l in range(len(mutantes)):
            print("Mutante {}:".format(l+1))
            print(mutantes[l])
            print(" ")
        print("-----------------------------------------")

        evoluidos = alg.crossover(alg.individuos, mutantes)

        for l in range(len(evoluidos)):
            print("Evoluido {}:".format(l+1))
            print(evoluidos[l])
            print(" ")
        print("-----------------------------------------")

        #vetor de rejeitados para reciclagem caso ocorra duplicação
        evoluidos_rejeitados = []

        for j in range(alg.num_individuos):
            individuo_evoluido = Individuo(evoluidos[j], alg.componentes, alg.peso_max, alg.custo_max, alg.coeficiente_peso, alg.coeficiente_custo)
            fit_evoluido = individuo_evoluido.valor_funcao_objetivo
            fit_individuo = alg.individuos[j].valor_funcao_objetivo

            if fit_evoluido > fit_individuo:
                alg.individuos[j].solucao = deepcopy(individuo_evoluido.solucao)
            else:
                evoluidos_rejeitados.append(deepcopy(individuo_evoluido))
            
            if fit_evoluido > melhor_solucao:
                melhor_solucao = fit_evoluido
                melhor_solucao_log = math.log(fit_evoluido)
                geracao = i + 1

        solucoes.append(melhor_solucao)
        solucoes_log.append(melhor_solucao_log)

        alg.individuos = alg.verifica_duplicados(alg.individuos)
        if(len(alg.individuos) < alg.num_individuos):
            #significa que precisamos completar a população
            evoluidos_rejeitados = sorted(evoluidos_rejeitados, key=lambda x: x.valor_funcao_objetivo, reverse=True)
            for k in range(alg.num_individuos - len(alg.individuos)):
                alg.individuos.append(evoluidos_rejeitados[k])

        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")

    alg.individuos = sorted(alg.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)
    melhor_individuo = alg.individuos[0]

    print("O algoritmo de evolução diferencial obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, alg.individuos[0].solucao[0][z]))
        print("Q{}: {}".format(z+1, alg.individuos[0].solucao[1][z]))
    print("\n")


    # Plotando o gráfico
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(0, alg.num_geracoes+1), solucoes, color='green')  # Linha verde plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (DE)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(melhor_solucao, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./DE/img/SolutionEvolutionDE.png')
    plt.show()

    # Plotando o gráfico em log
    plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='green')  # Linha verde plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('log(Função Objetivo)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (DE)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./DE/img/SolutionEvolutionDELog.png')
    plt.show()

    return solucoes_log, valor_final_log, melhor_individuo, geracao
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    