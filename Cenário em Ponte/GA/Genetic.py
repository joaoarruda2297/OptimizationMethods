import numpy as np
import math
from decimal import Decimal, getcontext
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt

class GeneticAlgorithm:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes):
        #variáveis para execução do algoritmo genético
        self.num_individuos = 50
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = num_geracoes
        self.taxa_cruzamento = 0.6 #quantidade de pais que gerarão individuos (pais/2)
        self.taxa_mutacao = 0.3 #quantidade de individuos que vão receber mutação

        self.num_tipos_componentes = componentes.shape[1]
        self.individuos = individuos
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
        confiabilidade = Decimal(self.confiabilidade_ponte(individuo))

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
        pop_avaliada = self.avaliacao_populacao(self.individuos)

        #print(self.individuos)

        populacao = sorted(pop_avaliada, key=lambda x: x[0], reverse=True)
        return populacao

    def seleciona_pais(self, populacao):
        #selecionando os pais de forma simples, apenas pelos mais fortes
        num_pais = int(self.taxa_cruzamento*self.num_individuos)

        if(num_pais % 2 != 0):
            num_pais-=1

        pais = []
        for i in range(num_pais):
            pais.append(populacao[i])


        return pais

    def crossover(self, pais):
        filhos = []

        for i in range(0, len(pais) - 1, 2):
            taxa_crossover = np.random.randint(1,self.num_variaveis-1)
            parte1 = pais[i][2][:, :taxa_crossover]
            parte2 = pais[i+1][2][:, taxa_crossover:]
            filho = np.hstack((parte1, parte2))
            filhos.append(filho)

        filhosavaliados = self.avaliacao_populacao(filhos)

        return filhosavaliados

    def seleciona_mutantes(self, populacao):
        #selecionando os mutantes de forma simples, apenas pelos mais fracos
        num_mutantes = int(self.taxa_mutacao*self.num_individuos)
        ind_para_mutacao = [deepcopy(populacao[i]) for i in range(self.num_individuos-1, self.num_individuos - num_mutantes -1, -1)]
        
        return ind_para_mutacao
    
    def mutacao(self, ind_para_mutacao):
        mutantes = []
        
        for i in range(len(ind_para_mutacao)):
            taxa_muta = 1 #quantos genes serão mudados
            index_subsistema = np.random.choice(self.num_variaveis, size=taxa_muta, replace=False) #quais genes serão mudados
            index_componente = np.random.choice(self.num_max_componentes_subsistema, size=taxa_muta, replace=False)

            for k in range(taxa_muta):
                operation = np.random.randint(0,5) #qual será a operação realizada em cima do gene, se for do tipo 1, exclui componente
                
                if operation == 1:
                    ind_para_mutacao[i][2][index_subsistema, index_componente] = -1
                else:
                    value = np.random.randint(0, self.num_tipos_componentes) #qual componente entrará no lugar
                    while value == ind_para_mutacao[i][2][index_subsistema, index_componente]:#garantindo que troque por um valor diferente
                        value = np.random.randint(0, self.num_tipos_componentes)
                    ind_para_mutacao[i][2][index_subsistema, index_componente] = value
            
            mutantes.append(ind_para_mutacao[i][2])

        mutantesavaliados = self.avaliacao_populacao(mutantes)
            
        return mutantesavaliados

    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(componentes, individuos, peso_max, custo_max, num_geracoes):
    alg = GeneticAlgorithm(componentes, individuos, peso_max, custo_max, num_geracoes)
    populacao = alg.inicia_populacao()

    solucoes = []
    solucoes_log = []
    melhor_solucao_log = -10000
    melhor_solucao = -10000
    geracao = -1
    geracao_log = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        if i == 0:
            for j in range(len(populacao)):
                log_individuo = math.log(populacao[j][1])

                if log_individuo > melhor_solucao_log:
                    melhor_solucao_log = log_individuo
                    print("MELHOR:", melhor_solucao_log)
            solucoes_log.append(melhor_solucao_log)
            geracao_log = 0

        if populacao[0][0] > melhor_solucao and i == 0:
            melhor_solucao = populacao[0][0]
            geracao = i
            solucoes.append(populacao[0][0])

        pais = alg.seleciona_pais(populacao)
        filhos = alg.crossover(pais)
    
        for l in range(len(filhos)):
            print("Filho {}:".format(l+1))
            print("FuncObj: {}".format(filhos[l][0]))
            print("Confiabilidade: {}".format(filhos[l][1]))
            print("Cromossomo: {}".format(filhos[l][2]))
            print(" ")
        print("-----------------------------------------")

        ind_para_mutacao = alg.seleciona_mutantes(populacao)
        mutantes = alg.mutacao(ind_para_mutacao)

        for l in range(len(mutantes)):
            print("Mutante {}:".format(l+1))
            print("FuncObj: {}".format(mutantes[l][0]))
            print("Confiabilidade: {}".format(mutantes[l][1]))
            print("Cromossomo: {}".format(mutantes[l][2]))
            print(" ")
        print("-----------------------------------------")

        print("Populacao antes da mescla:")
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(populacao[l][0]))
            print("Confiabilidade: {}".format(populacao[l][1]))
            print("Cromossomo: {}".format(populacao[l][2]))
            print(" ")
        print("-----------------------------------------")

        populacao = populacao + mutantes + filhos
        populacao = sorted(populacao, key=lambda x: x[0], reverse=True)

        populacao = populacao[:alg.num_individuos]
        print("Populacao final da era:")
        for l in range(len(populacao)):
            print("Filho {}:".format(l+1))
            print("FuncObj: {}".format(populacao[l][0]))
            print("Confiabilidade: {}".format(populacao[l][1]))
            print("Cromossomo: {}".format(populacao[l][2]))
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

        solucoes.append(populacao[0][0])

        if populacao[0][0] > melhor_solucao:
            melhor_solucao = populacao[0][0]
            geracao = i
        
        for j in range(len(populacao)):
            log_individuo = math.log(populacao[j][1])

            if log_individuo > melhor_solucao_log:
                melhor_solucao_log = log_individuo
                geracao_log = i
        solucoes_log.append(melhor_solucao_log)
        
    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", populacao[0][0])
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, populacao[0][2][z]))
    print("\n")

    # Plotando o gráfico
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(0, alg.num_geracoes+1), solucoes, color='orange')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(populacao[0][0], 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./GA/img/SolutionEvolutionGA.png')
    plt.show()

    # Plotando o gráfico em log
    plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='orange')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('log(confiabilidade)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao_log)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./GA/img/SolutionEvolutionGALog.png')
    plt.show()

    return solucoes_log, valor_final_log


if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    