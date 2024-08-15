import numpy as np
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt

class ParticleSwarmOptimization:
    def __init__(self):
        self.num_particulas = 200
        self.num_variaveis = 10 #no minimo 4
        self.num_geracoes = 100
        self.exploracao_global = 0.25 #C2
        self.auto_exploracao = 0.3 #C1
        self.taxa_inercia = 0.2 #w
        self.lim_sup = 5.0
        self.lim_inf = -5.0          

    def avaliacao(self, vetor):#funcao objetivo aqui!!!
        #para avaliar ele é necessário que olhemos para posicao em que se encontra, logo populacao[0][1]
        valoravaliado = np.sum(vetor**2)
        return valoravaliado

    def inicia_populacao(self):
        popinicial = np.random.uniform(self.lim_inf, self.lim_sup, ( self.num_particulas, 3, self.num_variaveis))

        # Copiar a segunda linha para a terceira linha para cada indivíduo
        # pois inicialmente a melhor posicao é a posicao atual
        for i in range(self.num_particulas):
            popinicial[i, 2] = popinicial[i, 1]

        #print(popinicial)

        #atenção!!!
        #populacao[0] retorna os 3 vetores de uma partícula
        #populacao[0][0] retorna vetor velocidade
        #populacao[0][1] retorna vetor position da particula
        #populacao[0][2] retorna vetor best position da partícula
        
        return popinicial
    
    def atualiza_velocidade(self, vecVeloc, vecPos, bestPos, globalBest):
        r1 = np.random.rand()
        r2 = np.random.rand()

        velocidade_final = (
            self.taxa_inercia*vecVeloc +
            self.auto_exploracao*r1*(bestPos - vecPos) + 
            self.exploracao_global*r2*(globalBest - vecPos)
        )
        return velocidade_final

    def atualiza_posicao(self, vecVeloc, vecPos):
        posicao_final = (
            vecPos + vecVeloc
        )

        #tratativa para caso ultrapasse os limites
        for i in range(len(posicao_final)):
            if posicao_final[i] > self.lim_sup:
                posicao_final[i] = float(self.lim_sup)
            elif posicao_final[i] < self.lim_inf:
                posicao_final[i] = float(self.lim_inf)

        return posicao_final

def main():
    alg = ParticleSwarmOptimization()
    populacao = alg.inicia_populacao()

    solucoes = []

    global_best = np.full(alg.num_variaveis, alg.lim_inf) if abs(alg.lim_inf) > abs(alg.lim_sup) else np.full(alg.num_variaveis, alg.lim_sup)
    melhor_solucao = alg.avaliacao(global_best)

    geracao = -1
    
    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        for j in range(alg.num_particulas):
            fit_pos_atual = alg.avaliacao(populacao[j][1])
            fit_best_pos = alg.avaliacao(populacao[j][2])
            fit_global = alg.avaliacao(global_best)

            if fit_pos_atual < fit_best_pos:
                populacao[j][2] = populacao[j][1]
            
            if fit_best_pos < fit_global:
                global_best = populacao[j][2]

            
        
        print("Populacao antes da execucao:")
        for l in range(len(populacao)):
            print("Particula {}:".format(l+1))
            print("Posicao: {}".format(populacao[l][1]))
            print("Velocidade: {}".format(populacao[l][0]))
            print(" ")
        print("-----------------------------------------")

        for k in range(alg.num_particulas):
            populacao[k][0] = alg.atualiza_velocidade(populacao[k][0], populacao[k][1], populacao[k][2],global_best)
            populacao[k][1] = alg.atualiza_posicao(populacao[k][0], populacao[k][1])

        print("Populacao final da era:")
        for l in range(len(populacao)):
            print("Particula {}:".format(l+1))
            print("Posicao: {}".format(populacao[l][1]))
            print("Velocidade: {}".format(populacao[l][0]))
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

        fit_global = alg.avaliacao(global_best)
        solucoes.append(fit_global)

        if melhor_solucao > fit_global:
            melhor_solucao = fit_global
            geracao = i

    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, global_best[z]))

    # Plotando o gráfico
    plt.plot(range(1, alg.num_geracoes+1), solucoes)
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações')
    plt.grid(True)
    texto = "Valor final: " + str(round(melhor_solucao, 4)) + "\nAlcançado na geração: " + str(geracao) 
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    plt.tight_layout()
    plt.savefig('SolutionEvolutionPSO.png')
    plt.show()
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    