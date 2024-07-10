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
        self.CR = 0.6

    def avaliacao(self, vetor):#funcao objetivo aqui!
        vetor_array = np.array(vetor)
        valoravaliado = np.sum(vetor_array**2)
        return valoravaliado

    def inicia_populacao(self):
        popinicial = np.random.uniform(self.lim_inf, self.lim_sup, (self.num_individuos, self.num_variaveis))
        
        return popinicial

    def crossover(self, populacao, mutantes):
        novos_candidatos = []
        for i in range(len(populacao)):
            trial_vector = []
            l = np.random.randint(0, self.num_variaveis)
            for j in range(self.num_variaveis):
                r = np.random.rand()
                if r > self.CR and j != l:
                    trial_vector.append(populacao[i][j])
                elif r <= self.CR or j == l:
                    trial_vector.append(mutantes[i][j])
            novos_candidatos.append(trial_vector)
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

            mutantes.append(mutante)
                
        return mutantes
        


def main():
    alg = DifferentialEvolution()
    populacao = alg.inicia_populacao()

    solucoes = []
    melhor_solucao = (alg.lim_inf**2) * alg.num_variaveis if abs(alg.lim_inf) > abs(alg.lim_sup) else (alg.lim_sup**2) * alg.num_variaveis
    idx_melhor_solucao = -1
    geracao = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        mutantes = alg.mutacao(populacao)

        for l in range(len(mutantes)):
            print("Mutante {}:".format(l+1))
            print("FuncObj: {}".format(alg.avaliacao(mutantes[l])))
            print("Cromossomo: {}".format(mutantes[l]))
            print(" ")
        print("-----------------------------------------")

        evoluidos = alg.crossover(populacao, mutantes)

        for l in range(len(evoluidos)):
            print("Evoluido {}:".format(l+1))
            print("FuncObj: {}".format(alg.avaliacao(evoluidos[l])))
            print("Cromossomo: {}".format(evoluidos[l]))
            print(" ")
        print("-----------------------------------------")

        for j in range(alg.num_individuos):
            fit_evoluido = alg.avaliacao(evoluidos[j])
            fit_individuo = alg.avaliacao(populacao[j])

            if fit_evoluido < fit_individuo:
                populacao[j] = evoluidos[j]
        
        for l in range(len(populacao)):
            print("Individuo {}:".format(l+1))
            print("FuncObj: {}".format(alg.avaliacao(populacao[l])))
            print("Cromossomo: {}".format(populacao[l]))
            print(" ")
        print("-----------------------------------------")
        
        for k in range(alg.num_individuos):
            fit_vetor = alg.avaliacao(populacao[k])

            if fit_vetor < melhor_solucao:
                melhor_solucao = fit_vetor
                idx_melhor_solucao = k
                geracao = i
        
        solucoes.append(melhor_solucao)
            

    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, populacao[idx_melhor_solucao][z]))

    # Plotando o gráfico
    plt.plot(range(1, alg.num_geracoes+1), solucoes)
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações')
    plt.grid(True)
    texto = "Valor final: " + str(round(melhor_solucao, 4)) + "\nAlcançado na geração: " + str(geracao) 
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    plt.tight_layout()
    plt.savefig('SolutionEvolutionDE.png')
    plt.show()
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    