import numpy as np
import math
from decimal import Decimal, getcontext
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt

class GeneticAlgorithm:
    def __init__(self):
        #variáveis para execução do algoritmo genético
        self.num_individuos = 50
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = 100
        self.taxa_cruzamento = 0.6 #quantidade de pais que gerarão individuos (pais/2)
        self.taxa_mutacao = 0.3 #quantidade de individuos que vão receber mutação

        #variáveis para geração de banco de dados de componentes
        self.num_tipos_componentes = 25
        self.lim_sup_peso = 15
        self.lim_inf_peso = 0
        self.lim_sup_custo = 25
        self.lim_inf_custo = 0
        self.peso_max = 120
        self.custo_max = 80

        self.num_max_componentes_subsistema = 10
        self.num_min_componentes_subsistema = 3

        self.coeficiente_custo = 1.1
        self.coeficiente_peso = 1.05
        
        self.componentes = self.cria_componentes()

    def cria_componentes(self):
        linha1 = np.round(np.random.uniform(0.9, 0.95, self.num_tipos_componentes), 8)  # confiabilidade com max 8 casas decimais
        linha2 = np.random.randint(self.lim_inf_custo + 1, self.lim_sup_custo + 1, self.num_tipos_componentes)#custo
        linha3 = np.random.randint(self.lim_inf_peso + 1, self.lim_sup_peso + 1, self.num_tipos_componentes)#peso
        
        # Combina as linhas em uma matriz
        matriz = np.vstack([linha1, linha2, linha3])
        return matriz

    def confiabilidade_paralelo(self, subsistema):
        getcontext().prec = 50
        confiabilidade = Decimal(1)

        for componente in subsistema:
            if componente != -1:
                conf_componente = Decimal(self.componentes[0][componente])
                confiabilidade = confiabilidade*(1 - conf_componente)
        print("\n")

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

        pop_avaliada = self.avaliacao_populacao(pop_inicial)

        populacao = sorted(pop_avaliada, key=lambda x: x[0], reverse=True)
        return populacao

    def seleciona_pais(self, populacao):
        #selecionando os pais de forma simples, apenas pelos mais fortes
        num_pais = int(self.taxa_cruzamento*self.num_individuos)

        if(num_pais % 2 != 0):
            num_pais-=1

        pais = [populacao[i] for i in range(num_pais)]

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

def main():
    alg = GeneticAlgorithm()
    populacao = alg.inicia_populacao()

    solucoes = []
    melhor_solucao = Decimal(-10000000)
    geracao = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

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
            print("Filho {}:".format(l+1))
            print("FuncObj: {}".format(mutantes[l][0]))
            print("Confiabilidade: {}".format(mutantes[l][1]))
            print("Cromossomo: {}".format(mutantes[l][2]))
            print(" ")
        print("-----------------------------------------")

        print("Populacao antes da mescla:")
        for l in range(len(populacao)):
            print("Filho {}:".format(l+1))
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
        
    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", populacao[0][0])
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, populacao[0][2][z]))
    print("\n")
    
    componentes_utilizados = []
    for z in range(alg.num_variaveis):
        for w in range(alg.num_max_componentes_subsistema):
            ganhador = populacao[0][2][z, w]
            if ganhador != -1 and ganhador not in componentes_utilizados:
                componentes_utilizados.append(ganhador)
                print(
                    "Componente {}:\n"
                    "Confiabilidade: {}\n"
                    "Custo: {}\n"
                    "Peso: {}\n"
                    .format(ganhador, alg.componentes[0][ganhador], alg.componentes[1][ganhador], alg.componentes[2][ganhador])
                )

    # Plotando o gráfico
    plt.axhline(y=0, color='red', linestyle='-', linewidth=0.5)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(1, alg.num_geracoes+1), solucoes, color='blue')  # Linha azul plotada depois

    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações')
    plt.grid(True)

    # Texto adicional no gráfico
    valor_final = alg.truncate(populacao[0][0], 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)

    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('SolutionEvolutionGA2.png')
    plt.show()


if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    