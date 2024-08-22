import numpy as np
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext
import math

class DifferentialEvolution:
    def __init__(self, componentes, peso_max, custo_max, num_geracoes):
        self.num_individuos = 50
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = num_geracoes
        self.passo = 1
        self.CR = 0.6

        self.num_tipos_componentes = componentes.shape[1]
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = 10
        self.num_min_componentes_subsistema = 3

        self.coeficiente_custo = 1.1
        self.coeficiente_peso = 1.05

    def confiabilidade_paralelo(self, subsistema):
        getcontext().prec = 50
        confiabilidade = Decimal(1)

        for componente in subsistema:
            if componente != -1:
                conf_componente = Decimal(self.componentes[0][componente])
                confiabilidade = confiabilidade*(1 - conf_componente)

        confiabilidade = 1 - confiabilidade
        return confiabilidade

    def confiabilidade_ponte(self, individuo):
        getcontext().prec = 50
        #considerando a confiabilidade do sistema em ponte
        r_1 = Decimal(self.confiabilidade_paralelo(individuo[0]))
        r_2 = Decimal(self.confiabilidade_paralelo(individuo[1]))
        r_3 = Decimal(self.confiabilidade_paralelo(individuo[2]))
        r_4 = Decimal(self.confiabilidade_paralelo(individuo[3]))
        r_5 = Decimal(self.confiabilidade_paralelo(individuo[4]))

        confiabilidade_sistema = Decimal(
            r_1*r_2 + r_3*r_4 + r_1*r_4*r_5 + r_2*r_3*r_5
            - r_1*r_2*r_3*r_4 - r_1*r_2*r_3*r_5 - r_1*r_2*r_4*r_5 - r_1*r_3*r_4*r_5 - r_2*r_3*r_4*r_5 
            + 2*r_1*r_2*r_3*r_4*r_5 
        )

        return confiabilidade_sistema

    def somatoria_custos(self, individuo):
        custo_total = 0
        for subsistema in individuo:
            for componente in subsistema:
                if componente != -1:
                    custo_total += self.componentes[1][componente]
        return custo_total

    def somatoria_pesos(self, individuo):
        peso_total = 0
        for subsistema in individuo:
            for componente in subsistema:
                if componente != -1:
                    peso_total += self.componentes[2][componente]
        return peso_total

    def funcao_objetivo(self, individuo):
        confiabilidade = self.confiabilidade_ponte(individuo)

        soma_pesos = self.somatoria_pesos(individuo)
        soma_custos = self.somatoria_custos(individuo)

        f_custo = soma_custos - self.custo_max
        f_peso =  soma_pesos - self.peso_max

        f_obj = confiabilidade - Decimal(self.coeficiente_peso*max(0, f_peso)) - Decimal(self.coeficiente_custo*max(0, f_custo))
        return f_obj

    def avaliacao_populacao(self, populacao):
        getcontext().prec = 50
        pop_avaliada = [(Decimal(self.funcao_objetivo(individuo)), Decimal(self.confiabilidade_ponte(individuo)), individuo) for individuo in populacao]
        return pop_avaliada

    def inicia_populacao(self):
        #gerando população inicial
        pop_inicial = np.random.randint(0, self.num_tipos_componentes, (self.num_individuos, self.num_variaveis, self.num_max_componentes_subsistema))

        #corrigindo quantos componentes cada subsistema irá ter
        for individuo in pop_inicial:
            for subsistema in individuo:
                num_componentes = np.random.randint(self.num_min_componentes_subsistema, self.num_max_componentes_subsistema+1)
                subsistema[num_componentes:] = -1

        #pop_avaliada = self.avaliacao_populacao(pop_inicial)
        #populacao = sorted(pop_avaliada, key=lambda x: x[0], reverse=True)
        return pop_inicial

    def crossover(self, populacao, mutantes):
        novos_candidatos = []
        for i in range(len(populacao)):
            trial_matrix = np.zeros((self.num_variaveis, self.num_max_componentes_subsistema), dtype=int)
            for k in range(self.num_variaveis):
                l = np.random.randint(0, self.num_variaveis)
                for j in range(self.num_max_componentes_subsistema):
                    r = np.random.rand()
                    if r > self.CR and j != l:
                        trial_matrix[k][j] = populacao[i][k][j]
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
                random_index = np.random.randint(0, self.num_variaveis)
                alreadyExists = False
                for j in range(len(idx)):
                    if idx[j] == random_index:
                        alreadyExists = True
                        break
                if alreadyExists is False:
                    idx.append(random_index)

            #gerando mutante
            mutante = (
                populacao[idx[1]] + 
                self.passo*(populacao[idx[3]] - populacao[idx[2]])
                )
            
            for j in range(self.num_variaveis):
                for k in range(self.num_max_componentes_subsistema):
                    if mutante[j][k] < -1:
                        mutante[j][k] = -1
                    elif mutante[j][k] >= self.num_tipos_componentes:
                        mutante[j][k] = self.num_tipos_componentes - 1

            mutantes.append(mutante)
        
        return mutantes
        
    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor


def main(componentes, peso_max, custo_max, num_geracoes):
    alg = DifferentialEvolution(componentes, peso_max, custo_max, num_geracoes)
    populacao = alg.inicia_populacao()

    solucoes = []
    melhor_solucao = -10000
    idx_melhor_solucao = -1
    geracao = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        mutantes = alg.mutacao(populacao)

        for l in range(len(mutantes)):
            print("Mutante {}:".format(l+1))
            print("FuncObj: {}".format(alg.funcao_objetivo(mutantes[l])))
            print("Cromossomo: \n{}".format(mutantes[l]))
            print(" ")
        print("-----------------------------------------")

        evoluidos = alg.crossover(populacao, mutantes)

        for l in range(len(evoluidos)):
            print("Evoluido {}:".format(l+1))
            print("FuncObj: {}".format(alg.funcao_objetivo(evoluidos[l])))
            print("Cromossomo: {}".format(evoluidos[l]))
            print(" ")
        print("-----------------------------------------")

        for j in range(alg.num_individuos):
            fit_evoluido = alg.funcao_objetivo(evoluidos[j])
            fit_individuo = alg.funcao_objetivo(populacao[j])

            fit_vetor = fit_individuo
            if fit_evoluido > fit_individuo:
                populacao[j] = evoluidos[j]
                fit_vetor = fit_evoluido
            
            if fit_vetor > melhor_solucao:
                melhor_solucao = fit_vetor
                idx_melhor_solucao = j
                geracao = i

        solucoes.append(melhor_solucao)
        
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(alg.funcao_objetivo(populacao[l])))
            print("Cromossomo: {}".format(populacao[l]))
            print(" ")
        print("-----------------------------------------")

    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, populacao[idx_melhor_solucao][z]))


    # Plotando o gráfico
    plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(1, alg.num_geracoes+1), solucoes, color='green')  # Linha azul plotada depois

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

    return solucoes, valor_final
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    