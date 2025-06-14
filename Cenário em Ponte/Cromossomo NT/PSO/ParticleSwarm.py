import numpy as np
import sys
import os
import math
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GeradorIndividuos import IndividuoPSO

class ParticleSwarmOptimization:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        self.num_particulas = len(individuos)
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = num_geracoes
        self.exploracao_global = 0.6 #C2
        self.auto_exploracao = 0.3 #C1
        self.taxa_inercia = 0.2 #w

        self.num_tipos_componentes = componentes.shape[1]
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = 10
        self.num_min_componentes_subsistema = 3

        self.coeficiente_custo = coeficiente_custo
        self.coeficiente_peso = coeficiente_peso

        self.individuos = []
        for i in range(len(individuos)):
            self.individuos.append(IndividuoPSO(individuos[i].solucao, componentes, None, peso_max, custo_max, coeficiente_peso, coeficiente_custo, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema))
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)
    
    def atualiza_velocidade(self, individuo, globalBest):
        r1 = np.random.rand()
        r2 = np.random.rand()

        inercia = deepcopy(individuo.velocidade)*self.taxa_inercia
        auto_exploracao = self.auto_exploracao*r1*(deepcopy(individuo.melhor_posicao.solucao) - deepcopy(individuo.solucao))
        exploracao_global = self.exploracao_global*r2*(deepcopy(globalBest.solucao) - deepcopy(individuo.solucao))

        velocidade_final = np.array(
            inercia + auto_exploracao + exploracao_global
        )

        return velocidade_final

    def atualiza_posicao(self, individuo):
        posicao_final = (
            deepcopy(individuo.solucao) + deepcopy(individuo.velocidade)
        )

        posicao_final_inteira = np.round(posicao_final,0)
        posicao_final_inteira[posicao_final_inteira == -0.0] = 0
        posicao_final_inteira[posicao_final_inteira >= 100] = 99  

        '''#tratativa para caso ultrapasse os limites
        #considerando os tipos de componente como um circulo fechado,
        #logicamente, se algum indice da posicao final possui um numero maior que num_tipos_componentes, ele volta ao 0 e vai somando
        #para encontrar o valor sobressalente.
        for i, subsistema in enumerate(posicao_final_inteira):
            for j, componente in enumerate(subsistema):
                if posicao_final_inteira[i][j] >= self.num_tipos_componentes:
                    while posicao_final_inteira[i][j] >= self.num_tipos_componentes:
                        posicao_final_inteira[i][j] -= self.num_tipos_componentes
                elif posicao_final_inteira[i][j] <= -1:
                    posicao_final_inteira[i][j] = -1'''

        return posicao_final_inteira
    
    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    alg = ParticleSwarmOptimization(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    solucoes = []
    solucoes_log = []
    geracao = -1
    geracao_log = -1

    global_best = None
    melhor_solucao = -10000
    melhor_solucao_log = -10000

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))
        for j in range(alg.num_particulas):
            fit_pos_atual = alg.individuos[j].valor_funcao_objetivo
            fit_best_pos = alg.individuos[j].melhor_posicao.valor_funcao_objetivo

            if i == 0 and j==0:
                fit_global = -10000
            else:
                fit_global = global_best.valor_funcao_objetivo
                
            if fit_pos_atual > fit_best_pos:
                alg.individuos[j].melhor_posicao = deepcopy(alg.individuos[j])
                fit_best_pos = alg.individuos[j].melhor_posicao.valor_funcao_objetivo
            
            if fit_best_pos > fit_global:
                global_best = deepcopy(alg.individuos[j].melhor_posicao)
                fit_global = fit_best_pos

        if i == 0: solucoes_log.append(math.log(fit_global))
        
        print("Populacao antes da execucao:")
        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")

        for k in range(alg.num_particulas):
            if i != 0:
                alg.individuos[k].velocidade = alg.atualiza_velocidade(alg.individuos[k], global_best)
            alg.individuos[k].solucao = alg.atualiza_posicao(alg.individuos[k])

        print("Populacao final da era:")
        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

        fit_global = global_best.valor_funcao_objetivo
        solucoes.append(fit_global)
        solucoes_log.append(math.log(fit_global))

        if melhor_solucao < fit_global:
            melhor_solucao_log = math.log(fit_global)
            melhor_solucao = fit_global
            geracao = i
            geracao_log = i
            
    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, alg.individuos[0].solucao[0][z]))
        print("Q{}: {}".format(z+1, alg.individuos[0].solucao[1][z]))
    print("\n")

    # Plotando o gráfico
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(1, alg.num_geracoes+1), solucoes, color='purple')  # Linha roxa plotada depois
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

    # Plotando o gráfico em log
    plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='purple')  # Linha roxa plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('log(confiabilidade)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (PSO)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao_log)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./PSO/img/SolutionEvolutionPSOLog.png')
    plt.show()

    return solucoes_log, valor_final_log
        

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    