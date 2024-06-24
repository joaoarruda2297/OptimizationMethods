import numpy as np

class GenteticAlgorithm:
    def __init__(self):
        self.num_individuos = 100
        self.num_variaveis = 10
        self.num_geracoes = 100
        self.taxa_cruzamento = 0.5
        self.taxa_mutacao = 0.1
        self.num_elite = 10
        self.lim_sup = 5
        self.lim_inf = -5

    def inicia_populacao(self):
        popinicial = np.random.uniform(self.lim_inf, self.lim_sup, (self.num_individuos, self.num_variaveis))
        popinicial = np.round(popinicial, decimals=6)

        popavaliada = [(np.sum(individuo), individuo) for individuo in popinicial]

        populacao = sorted(popavaliada, key=lambda x: abs(x[0]))
        
        return populacao

def main():
    alg = GenteticAlgorithm()
    populacao = alg.inicia_populacao()
    


if __name__ == "__main__":
    main()