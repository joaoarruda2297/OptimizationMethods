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
        

    def inicia_populacao(self):
        

    def seleciona_pais(self, populacao):
        

    def crossover(self, pais):
        
    
    def seleciona_mutantes(self, populacao):
        

    def mutacao(self, ind_para_mutacao):
        


def main():
    alg = GeneticAlgorithm()
    populacao = alg.inicia_populacao()

    solucoes = []
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
    plt.show()
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    