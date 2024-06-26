import numpy as np
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt

class GeneticAlgorithm:
    def __init__(self):
        self.num_individuos = 500
        self.num_variaveis = 10 #no minimo 4
        self.num_geracoes = 100
        self.taxa_cruzamento = 0.6 #quantidade de pais que gerarão individuos (pais/2)
        self.taxa_mutacao = 0.3 #quantidade de individuos que vão receber mutação
        self.lim_sup = 5.0
        self.lim_inf = -5.0

    def avaliacao(self, vetor):#funcao objetivo aqui!!!
        vetoravaliado = [(np.sum(individuo**2), individuo) for individuo in vetor]
        return vetoravaliado

    def inicia_populacao(self):
        popinicial = np.random.uniform(self.lim_inf, self.lim_sup, (self.num_individuos, self.num_variaveis))

        popavaliada = self.avaliacao(popinicial)

        populacao = sorted(popavaliada, key=lambda x: abs(x[0]))
        
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
            taxa_crossover = np.random.randint(0,self.num_variaveis-1)
            parte1 = pais[i][1][:taxa_crossover]
            parte2 = pais[i+1][1][taxa_crossover:]
            filho = np.concatenate((parte2, parte1))
            filhos.append(filho)
        
        filhosavaliados = self.avaliacao(filhos)

        return filhosavaliados
    
    def seleciona_mutantes(self, populacao):
        #selecionando os mutantes de forma simples, apenas pelos mais fracos
        num_mutantes = int(self.taxa_mutacao*self.num_individuos)
        #gambiarra com deepcopy, olhar pra arrumar
        ind_para_mutacao = [deepcopy(populacao[i]) for i in range(self.num_individuos-1, self.num_individuos - num_mutantes -1, -1)]
        
        return ind_para_mutacao

    def mutacao(self, ind_para_mutacao):
        mutantes = []
        
        for i in range(len(ind_para_mutacao)):
            taxa_muta = np.random.randint(1,int(self.num_variaveis/2)) #quantos genes serão mudados
            genes = np.random.choice(self.num_variaveis, size=taxa_muta, replace=False) #quais genes serão mudados

            for k in range(taxa_muta):
                add_sub = np.random.randint(0,2) #qual será a operação realizada em cima do gene
                value = np.random.uniform(self.lim_inf, self.lim_sup) #qual valor será aplicada a operação em cima do gene

                if add_sub == 0:
                    ind_para_mutacao[i][1][genes[k]] += value
                else:
                    ind_para_mutacao[i][1][genes[k]] -= value

                if abs(ind_para_mutacao[i][1][genes[k]]) > self.lim_sup: #garantindo que não ultrapasse os limites
                    if ind_para_mutacao[i][1][genes[k]] > 0:
                        ind_para_mutacao[i][1][genes[k]] = float(self.lim_sup)
                    elif ind_para_mutacao[i][1][genes[k]] < 0:
                        ind_para_mutacao[i][1][genes[k]] = float(self.lim_inf)
            
            mutantes.append(ind_para_mutacao[i][1])

        mutantesavaliados = self.avaliacao(mutantes)
            
        return mutantesavaliados


def main():
    alg = GenteticAlgorithm()
    populacao = alg.inicia_populacao()

    solucoes = []
    melhor_solucao = (alg.lim_inf**2) * alg.num_variaveis if abs(alg.lim_inf) > abs(alg.lim_sup) else (alg.lim_sup**2) * alg.num_variaveis
    geracao = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        pais = alg.seleciona_pais(populacao)
        filhos = alg.crossover(pais)

        for l in range(len(filhos)):
            print("Filho {}:".format(l+1))
            print("FuncObj: {}".format(filhos[l][0]))
            print("Cromossomo: {}".format(filhos[l][1]))
            print(" ")
        print("-----------------------------------------")

        ind_para_mutacao = alg.seleciona_mutantes(populacao)
        mutantes = alg.mutacao(ind_para_mutacao)

        for l in range(len(mutantes)):
            print("Mutante {}:".format(l+1))
            print("FuncObj: {}".format(mutantes[l][0]))
            print("Cromossomo: {}".format(mutantes[l][1]))
            print(" ")
        print("-----------------------------------------")
        
        print("Populacao antes da mescla:")
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(populacao[l][0]))
            print("Cromossomo: {}".format(populacao[l][1]))
            print(" ")
        print("-----------------------------------------")
        populacao = populacao + mutantes + filhos
        
        print("Populacao depois da mescla e antes de ordenar:")
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(populacao[l][0]))
            print("Cromossomo: {}".format(populacao[l][1]))
            print(" ")
        print("-----------------------------------------")
        
        populacao = sorted(populacao, key=lambda x: abs(x[0]))

        print("Populacao depois de ordenar e andar de elitizar:")
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(populacao[l][0]))
            print("Cromossomo: {}".format(populacao[l][1]))
            print(" ")
        print("-----------------------------------------")

        populacao = populacao[:alg.num_individuos]

        print("Populacao final da era:")
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(populacao[l][0]))
            print("Cromossomo: {}".format(populacao[l][1]))
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

        solucoes.append(populacao[0][0])

        if populacao[0][0] < melhor_solucao:
            melhor_solucao = populacao[0][0]
            geracao = i

    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", populacao[0][0])
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, populacao[0][1][z]))

    # Plotando o gráfico
    plt.plot(range(1, alg.num_geracoes+1), solucoes)
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações')
    plt.grid(True)
    texto = "Valor final: " + str(round(populacao[0][0], 4)) + "\nAlcançado na geração: " + str(geracao) 
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    plt.tight_layout()
    plt.savefig('SolutionEvolutionGA.png')
    plt.show()
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    