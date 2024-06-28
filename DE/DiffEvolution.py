import numpy as np
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt

class DifferentialEvolution:
    def __init__(self):
        self.num_individuos = 100
        self.num_variaveis = 4 #no minimo 4
        self.num_geracoes = 100
        self.lim_sup = 5.0
        self.lim_inf = -5.0
        self.passo = 1
        self.taxa_cruzamento = 0.6

    def avaliacao(self, individuo):#funcao objetivo aqui!!!
        valoravaliado = np.sum(individuo**2)
        return valoravaliado

    def inicia_populacao(self):
        popinicial = np.random.randint(self.lim_inf, self.lim_sup, (self.num_individuos, self.num_variaveis))
        
        return popinicial

    #def crossover(self, populacao, mutantes):
        #for i in range(len(populacao)):
            

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

            mutantes.append(mutante)
                
        return mutantes
        


def main():
    alg = DifferentialEvolution()
    populacao = alg.inicia_populacao()
    mutantes = alg.mutacao(populacao)
    evoluidos = alg.crossover(populacao, mutantes)

    '''solucoes = []
    melhor_solucao = (alg.lim_inf**2) * alg.num_variaveis if abs(alg.lim_inf) > abs(alg.lim_sup) else (alg.lim_sup**2) * alg.num_variaveis
    geracao = -1

    for i in range(alg.num_geracoes):

        

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
    plt.show()'''
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    