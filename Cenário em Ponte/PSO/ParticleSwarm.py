import numpy as np
import math
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext

class ParticleSwarmOptimization:
    def __init__(self, componentes, peso_max, custo_max, num_geracoes):
        self.num_particulas = 50
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = num_geracoes
        self.exploracao_global = 0.25 #C2
        self.auto_exploracao = 0.3 #C1
        self.taxa_inercia = 0.2 #w

        self.num_tipos_componentes = componentes.shape[1]
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = 10
        self.num_min_componentes_subsistema = 3

        self.coeficiente_custo = 1.1
        self.coeficiente_peso = 1.05
        
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

    def funcao_objetivo(self, individuo):
        confiabilidade = Decimal(self.confiabilidade_ponte(individuo))

        soma_pesos = self.somatoria_pesos(individuo)
        soma_custos = self.somatoria_custos(individuo)

        f_custo = soma_custos - self.custo_max
        f_peso =  soma_pesos - self.peso_max

        f_obj = confiabilidade - Decimal(self.coeficiente_peso*max(0, f_peso)) - Decimal(self.coeficiente_custo*max(0, f_custo))
        return f_obj

    def inicia_populacao(self):
        #cada individuo deve possui a matriz posicao, a matriz velocidade e a matriz de melhor posicao passada por ele
        popinicial = np.random.randint(0, self.num_tipos_componentes, ( self.num_particulas, 3, self.num_variaveis, self.num_max_componentes_subsistema))

        for individuo in popinicial:
            for matriz in individuo:
                for subsistema in matriz:
                    num_componentes = np.random.randint(self.num_min_componentes_subsistema, self.num_max_componentes_subsistema+1)
                    subsistema[num_componentes:] = -1

        # Copiar a primeira matriz para a terceira matriz para cada indivíduo
        # pois inicialmente a melhor posicao é a posicao atual
        for i in range(self.num_particulas):
            popinicial[i, 2] = popinicial[i, 0]

        #atenção!!!
        #populacao[0] retorna os 3 vetores de uma partícula
        #populacao[0][0] retorna vetor position da particula
        #populacao[0][1] retorna vetor velocidade
        #populacao[0][2] retorna vetor best position da partícula
        
        return popinicial
    
    def atualiza_velocidade(self, matrizVeloc, matrizPos, bestPos, globalBest):
        r1 = np.random.rand()
        r2 = np.random.rand()

        inercia = np.full((self.num_variaveis, self.num_max_componentes_subsistema), -1)
        for i, subsistema in enumerate(matrizVeloc):
            for j, componente in enumerate(subsistema):
                if componente != -1:
                    inercia[i][j] = matrizVeloc[i][j]*self.taxa_inercia
                else:
                    inercia[i][j] = -1

        auto_exploracao_t = np.full((self.num_variaveis, self.num_max_componentes_subsistema), -1)
        for i, subsistema in enumerate(bestPos):
            for j, componente in enumerate(subsistema):
                if componente != -1:
                    auto_exploracao_t[i][j] = self.auto_exploracao*r1*(bestPos[i][j] - matrizPos[i][j])
                else:
                    auto_exploracao_t[i][j] = -1

        exploracao_global_t = np.full((self.num_variaveis, self.num_max_componentes_subsistema), -1)
        for i, subsistema in enumerate(globalBest):
            for j, componente in enumerate(subsistema):
                if componente != -1:
                    exploracao_global_t[i][j] = self.exploracao_global*r1*(globalBest[i][j] - matrizPos[i][j])
                else:
                    exploracao_global_t[i][j] = -1
        
        velocidade_final = np.array(
            inercia + auto_exploracao_t + exploracao_global_t
        )

        return velocidade_final

    def atualiza_posicao(self, matrizVeloc, matrizPos):
        posicao_final = (
            matrizPos + matrizVeloc
        )

        posicao_final_inteira = np.round(posicao_final,0)
        posicao_final_inteira[posicao_final_inteira == -0.0] = 0

        #tratativa para caso ultrapasse os limites
        #considerando os tipos de componente como um circulo fechado,
        #logicamente, se algum indice da posicao final possui um numero maior que num_tipos_componentes, ele volta ao 0 e vai somando
        #para encontrar o valor sobressalente.
        for i, subsistema in enumerate(posicao_final_inteira):
            for j, componente in enumerate(subsistema):
                if posicao_final_inteira[i][j] >= self.num_tipos_componentes:
                    while posicao_final_inteira[i][j] >= self.num_tipos_componentes:
                        posicao_final_inteira[i][j] -= self.num_tipos_componentes
                elif posicao_final_inteira[i][j] <= -1:
                    posicao_final_inteira[i][j] = -1

        return posicao_final_inteira
    
    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(componentes, peso_max, custo_max, num_geracoes):
    alg = ParticleSwarmOptimization(componentes, peso_max, custo_max, num_geracoes)
    populacao = alg.inicia_populacao()

    solucoes = []
    geracao = -1

    global_best = np.full((alg.num_variaveis, alg.num_max_componentes_subsistema), -1)
    melhor_solucao = -10000

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        for j in range(alg.num_particulas):
            fit_pos_atual = alg.funcao_objetivo(populacao[j][0])
            fit_best_pos = alg.funcao_objetivo(populacao[j][2])

            if i == 0 and j==0:
                fit_global = -10000
            else:
                fit_global = alg.funcao_objetivo(global_best)
                
            if fit_pos_atual > fit_best_pos:
                populacao[j][2] = populacao[j][0]
            
            if fit_best_pos > fit_global:
                global_best = populacao[j][2]
                fit_global = fit_best_pos
        
        print("Populacao antes da execucao:")
        for l in range(len(populacao)):
            print("Particula {}:".format(l+1))
            print("Posicao: {}".format(populacao[l][1]))
            print("Velocidade: {}".format(populacao[l][0]))
            print(" ")
        print("-----------------------------------------")

        for k in range(alg.num_particulas):
            populacao[k][1] = alg.atualiza_velocidade(populacao[k][1], populacao[k][0], populacao[k][2],global_best)
            populacao[k][0] = alg.atualiza_posicao(populacao[k][1], populacao[k][0])

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

        fit_global = alg.funcao_objetivo(global_best)
        solucoes.append(fit_global)

        if melhor_solucao < fit_global:
            melhor_solucao = fit_global
            geracao = i
            
    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("x{}: {}".format(z+1, global_best[z]))

    # Plotando o gráfico
    plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(1, alg.num_geracoes+1), solucoes, color='purple')  # Linha azul plotada depois

    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (PSO)')
    plt.grid(True)

    # Texto adicional no gráfico
    valor_final = alg.truncate(melhor_solucao, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)

    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./PSO/img/SolutionEvolutionPSO.png')
    plt.show()

    return solucoes, valor_final
        

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    